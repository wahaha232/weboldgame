/* 楚漢之爭 — Web 可玩重製雛形 v1 (重製設定,未驗證規則) */
(function(){
"use strict";
var D = window.GAME_DATA;
var COLORS = ["#c0392b","#2e86c1","#27ae60","#8e44ad","#d4ac0d","#16a085",
              "#e67e22","#7f8c8d","#b03a2e"];
var NAMES9 = ["秦(胡亥)","劉邦","項梁","武臣","韓廣","魏咎","田儋","東勝","吳芮"];
var VICTORY_CITIES = 20;  // 重製勝利條件(未驗證)

var S=null, selCity=-1, selRuler=-1, svg=null;

function $(id){ return document.getElementById(id); }
function fmt(n){ return Math.floor(n); }
function log(msg){ var f=$("log"),d=document.createElement("div"); d.textContent=msg; f.appendChild(d); f.scrollTop=f.scrollHeight; }

function cityIndex(name){ return D.cities.findIndex(function(c){return c.n===name;}); }
function buildNeighbors(){
  D.cities.forEach(function(c){ c.nb=[]; });
  var th=15;
  D.cities.forEach(function(a){
    D.cities.forEach(function(b){
      if(a===b) return;
      var dx=a.x-b.x, dy=a.y-b.y;
      if(Math.sqrt(dx*dx+dy*dy) < th) a.nb.push(b.i);
    });
  });
  D.cities.forEach(function(a){
    if(a.nb.length===0){
      var best=null,bd=1e9;
      D.cities.forEach(function(b){ if(b!==a){ var dx=a.x-b.x,dy=a.y-b.y,d=dx*dx+dy*dy; if(d<bd){bd=d;best=b;} } });
      if(best) a.nb.push(best.i);
    }
  });
}

function makeState(ri){
  var qin=D.aiQin, rulers=D.rulers;
  S={year:1,month:1,factions:[],cities:[],sel:ri+1};
  S.factions.push({id:0,name:qin.n,face:qin.face,gold:qin.gold,food:qin.food,
                   isPlayer:false,truce:{},alive:true});
  rulers.forEach(function(r,k){
    S.factions.push({id:k+1,name:r.n,face:r.face,gold:r.gold,food:r.food,
                     isPlayer:(k===ri),truce:{},alive:true});
  });
  var caps=S.factions.map(function(f){ return cityIndex(f.id===0?qin.city:rulers[f.id-1].city); });
  D.cities.forEach(function(c){
    var best=0,bd=1e9;
    S.factions.forEach(function(f,k){
      var cc=D.cities[caps[k]], dx=cc.x-c.x, dy=cc.y-c.y, d=dx*dx+dy*dy;
      if(d<bd){bd=d;best=k;}
    });
    S.cities.push({i:c.i,o:best,army:500+Math.floor(Math.random()*500),
                   dev:10+Math.floor(Math.random()*30),acted:false});
  });
  recount(); 
}
function recount(){
  S.factions.forEach(function(f){ f.cityCount=0; });
  S.cities.forEach(function(c){ if(c.o>=0) S.factions[c.o].cityCount=(S.factions[c.o].cityCount||0)+1; });
}
function player(){ return S.factions[S.sel]; }

function attack(fromCityId,toCityId){
  var fc=S.cities[fromCityId], tc=S.cities[toCityId];
  if(fc.army<50){ log("兵力不足"); return; }
  if(tc.o===fc.o){
    var mv=Math.floor(fc.army*0.5); fc.army-=mv; tc.army+=mv;
    log("調兵 "+mv+" 至 "+D.cities[toCityId].n); fc.acted=true; render(); return;
  }
  var atk=fc.army*(0.85+Math.random()*0.3);
  var def=tc.army*(0.8+Math.random()*0.4);
  fc.army=Math.floor(fc.army*0.7);
  if(atk>def){
    tc.o=fc.o; tc.army=Math.floor((atk-def)*0.5); tc.dev=Math.max(1,tc.dev-5);
    log(NAMES9[fc.o]+" 攻下 "+D.cities[toCityId].n+"!");
  } else log(NAMES9[fc.o]+" 攻打 "+D.cities[toCityId].n+" 失敗");
  fc.acted=true; checkFactions(); render();
}
function defeatFaction(id){
  var f=S.factions[id];
  if((f.cityCount||0)>0) return;
  f.alive=false;
  S.cities.forEach(function(c){ if(c.o===id){ c.o=-1; c.army=Math.floor(c.army*0.8); } });
  log(NAMES9[id]+" 已滅亡。");
}
function checkFactions(){ S.factions.forEach(defeatFaction); recount(); }
function aiTurn(){
  S.factions.forEach(function(f,k){
    if(k===S.sel || !f.alive) return;
    S.cities.forEach(function(c){
      if(c.o===k && !c.acted && f.gold>400){
        var r=Math.min(300,Math.floor(f.gold*0.3)); f.gold-=r; c.army+=r; c.acted=true;
      }
    });
    var my=S.cities.filter(function(c){return c.o===k && c.army>800;});
    if(my.length){
      var from=my[Math.floor(Math.random()*my.length)];
      var cands=D.cities[from.i].nb.filter(function(t){
        var tc=S.cities[t];
        return tc.o>=0 && tc.o!==k && !(f.truce[tc.o]>0);
      });
      if(cands.length){
        var to=cands[Math.floor(Math.random()*cands.length)], t=S.cities[to];
        var atk=from.army*(0.85+Math.random()*0.3), def=t.army*(0.8+Math.random()*0.4);
        from.army=Math.floor(from.army*0.7);
        if(atk>def){ t.o=k; t.army=Math.floor((atk-def)*0.5); log(NAMES9[k]+" 攻下 "+D.cities[to].n); }
        else log(NAMES9[k]+" 攻打 "+D.cities[to].n+" 失敗");
      }
    }
  });
  checkFactions();
  S.factions.forEach(function(f){ for(var k in f.truce){ if(f.truce[k]>0) f.truce[k]--; } });
}
function endTurn(){
  var q=player();
  if((q.cityCount||0)===0){ log("已無領地,遊戲結束"); return; }
  S.month++;
  if(S.month>12){ S.month=1; S.year++; log("— 第"+S.year+"年 —"); }
  S.cities.forEach(function(c){
    if(c.o>=0 && S.factions[c.o].alive){
      var f=S.factions[c.o];
      f.gold+=40; f.food+=c.dev;
      if(c.o===S.sel && !c.acted){ c.army=Math.min(50000,c.army+Math.floor(c.dev*3)); }
    }
    c.acted=false;
  });
  recount();
  aiTurn();
  q=player(); recount();
  if((q.cityCount||0)>=VICTORY_CITIES){ alert("勝利!佔領 "+q.cityCount+" 城(重製條件)"); }
  if((q.cityCount||0)===0){ alert("你已滅亡…"); }
  log("— 第"+S.year+"年 第"+S.month+"月 —");
  render();
}
function doAction(cid,act){
  var p=player(), c=S.cities[cid];
  if(c.o!==S.sel || c.acted) return;
  if(act==="dev"){
    if(p.gold<30){ log("金不足"); return; }
    p.gold-=30; c.dev=Math.min(100,c.dev+3);
    log(D.cities[cid].n+" 開發(+3)");
  } else if(act==="recruit"){
    var maxUse=Math.min(p.gold, Math.max(0,50000-c.army));
    if(maxUse<5){ log("金不足或已滿"); return; }
    var cost=Math.min(1000,maxUse); p.gold-=cost; c.army+=cost;
    log(D.cities[cid].n+" 徵兵 +"+cost);
  }
  c.acted=true; render();
}
function cityTotal(){ var t=0; S.cities.forEach(function(c){ if(c.o===S.sel) t+=c.army; }); return t; }
function ownerName(id){ return id<0?"中立":NAMES9[id]; }
function render(){
  var p=player();
  $("pName").textContent=NAMES9[S.sel];
  $("faceSmall").src="img/face/face_"+String(p.face).padStart(2,"0")+".png";
  $("pStats").textContent="金 "+fmt(p.gold)+"  糧 "+fmt(p.food)+"  兵力 "+fmt(cityTotal())+"  城 "+((p.cityCount||0)+"/39");
  $("yearMon").textContent="楚漢 第"+S.year+"年 第"+S.month+"月";
  $("global").textContent="勝利條件:佔領 "+VICTORY_CITIES+" 城(重製設定)";
  drawMap(); renderCity(); renderDiplo();
}
function drawMap(){
  svg.innerHTML="";
  D.cities.forEach(function(c){
    var ct=S.cities[c.i];
    var g=document.createElementNS("http://www.w3.org/2000/svg","g");
    g.setAttribute("class","city");
    var cir=document.createElementNS("http://www.w3.org/2000/svg","circle");
    cir.setAttribute("cx",c.x); cir.setAttribute("cy",c.y); cir.setAttribute("r","2.3");
    cir.setAttribute("fill", ct.o<0?"#666":COLORS[ct.o]);
    cir.setAttribute("stroke","#000"); cir.setAttribute("stroke-width","0.4");
    g.appendChild(cir);
    var t=document.createElementNS("http://www.w3.org/2000/svg","text");
    t.setAttribute("x",c.x); t.setAttribute("y",Math.max(3,c.y-2.7));
    t.setAttribute("text-anchor","middle"); t.setAttribute("fill","#e8e4d8");
    t.textContent=c.n; g.appendChild(t);
    g.addEventListener("click",(function(i){return function(){selCity=i; renderCity();};})(c.i));
    svg.appendChild(g);
  });
}
function renderCity(){
  if(selCity<0){ $("cityTitle").textContent="選取城市"; $("cityInfo").innerHTML="點地圖上的城市查看/下指令"; $("cityActions").innerHTML=""; return; }
  var c=S.cities[selCity], mc=D.cities[selCity];
  $("cityTitle").textContent=mc.n;
  $("cityInfo").innerHTML="勢力:"+ownerName(c.o)+"  兵力:"+fmt(c.army)+"  開發:"+c.dev+
    "<br/>鄰接:"+mc.nb.map(function(i){return D.cities[i].n;}).join("、");
  var h=$("cityActions"); h.innerHTML="";
  if(c.o===S.sel){
    if(!c.acted){
      h.innerHTML+='<button class="small" onclick="G.doAction('+selCity+',\'dev\')">開發(金30)</button>';
      h.innerHTML+='<button class="small" onclick="G.doAction('+selCity+',\'recruit\')">徵兵</button>';
      h.innerHTML+='<div>出兵至:</div>';
      mc.nb.forEach(function(i){ var t=S.cities[i];
        h.innerHTML+='<button class="small" onclick="G.attack('+selCity+','+i+')">'+(t.o===S.sel?"調兵→":"攻→")+D.cities[i].n+'</button>'; });
    } else h.innerHTML="<em>本城本回合已行動</em>";
  } else h.innerHTML="<em>非己方城市</em>";
}
function renderDiplo(){
  var sel=$("diploTarget"); sel.innerHTML="";
  S.factions.forEach(function(f,k){
    if(k!==S.sel && f.alive){ var o=document.createElement("option"); o.value=k; o.textContent=NAMES9[k]; sel.appendChild(o); }
  });
}
function newGame(ri){
  makeState(ri);
  $("picker").classList.add("hidden"); $("menu").classList.add("hidden");
  $("game").classList.remove("hidden"); selCity=-1;
  log("開始:你是 "+NAMES9[S.sel]+",駐地 "+D.rulers[ri].city);
  log("※ 重製設定:座標/起始/勝利條件未經原版驗證");
  render();
}
function saveGame(){ try{ localStorage.setItem("han-web-remake",JSON.stringify(S)); log("已存檔"); }catch(e){ log("存檔失敗"); } }
function loadGame(){
  var raw=localStorage.getItem("han-web-remake");
  if(!raw){ alert("無存檔"); return; }
  S=JSON.parse(raw);
  $("picker").classList.add("hidden"); $("menu").classList.add("hidden");
  $("game").classList.remove("hidden"); selCity=-1;
  log("讀檔完成"); render();
}
function bind(){
  svg=$("map");
  buildNeighbors();
  $("btnNew").onclick=function(){
    var list=$("rulerList"); list.innerHTML="";
    D.rulers.forEach(function(r,k){
      var d=document.createElement("div"); d.className="ruler";
      d.innerHTML='<img src="img/face/face_'+String(r.face).padStart(2,"0")+'.png"/><div><b>'+r.n+'</b></div><small>駐地:'+r.city+'</small>';
      d.onclick=function(){ selRuler=k; for(var i=0;i<list.children.length;i++) list.children[i].classList.remove("sel"); d.classList.add("sel"); };
      list.appendChild(d);
    });
    $("menu").classList.add("hidden"); $("picker").classList.remove("hidden");
  };
  $("btnStart").onclick=function(){ if(selRuler<0){ alert("請選擇君主"); return; } newGame(selRuler); };
  $("btnLoad").onclick=loadGame;
  $("btnTurn").onclick=endTurn;
  $("btnSave").onclick=saveGame;
  $("btnDiplo").onclick=function(){
    var p=player(), k=parseInt($("diploTarget").value,10);
    if(p.gold<1000){ log("金不足"); return; }
    p.gold-=1000; p.truce[k]=10; S.factions[k].truce[S.sel]=10;
    log("與 "+NAMES9[k]+" 停戰(10回合)"); render();
  };
  $("btnMenu2").onclick=function(){ $("game").classList.add("hidden"); $("menu").classList.remove("hidden"); };
  window.G={doAction:doAction,attack:attack};
}
window.addEventListener("DOMContentLoaded",bind);
})();


