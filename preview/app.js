"use strict";
// Public preview only. Data is deliberately fictional and never sent to a server.
const tenants = {
  island:{name:"Island Family Clinic",country:"Saint Lucia",region:"Caribbean",currency:"USD",patients:[
    ["Avery Charles","Diabetes management","Stable","2026-10-30","7.2 mmol/L"],
    ["Jordan Pierre","Hypertension","Review","2026-10-29","132/82 mmHg"],
    ["Taylor Joseph","Post-discharge","Stable","2026-10-30","97% SpO₂"],
    ["Morgan James","General monitoring","Alert","2026-10-28","142/92 mmHg"]],observations:[12,17,20,22,26,28,31,36,34,42,49,46],alerts:2,users:6},
  maple:{name:"Maple Care Network",country:"Canada",region:"Canada",currency:"CAD",patients:[
    ["Alex Morgan","Hypertension","Stable","2026-10-30","124/78 mmHg"],
    ["Casey Bennett","Diabetes management","Review","2026-10-29","8.1 mmol/L"],
    ["Riley Chen","Cardiac follow-up","Stable","2026-10-30","76 bpm"]],observations:[9,10,12,14,17,19,24,27,30,31,35,38],alerts:1,users:4},
  bay:{name:"Bay Medical Group",country:"United States",region:"United States",currency:"USD",patients:[
    ["Cameron Davis","Post-discharge","Review","2026-10-30","98% SpO₂"],
    ["Harper Lane","Diabetes management","Stable","2026-10-30","118 mg/dL"],
    ["Sam Rivera","Hypertension","Alert","2026-10-29","151/96 mmHg"],
    ["Drew Parker","Cardiac follow-up","Stable","2026-10-30","71 bpm"],
    ["Skyler Reed","General monitoring","Stable","2026-10-28","36.8 °C"]],observations:[8,13,18,21,23,25,29,33,37,43,50,54],alerts:3,users:9}
};
const modules=[
  ["📊","Remote patient monitoring","Organize observations, care plans, and clinical follow-up. Device feeds require separate integration and validation."],
  ["🩺","Virtual care","Plan appointments, secure team workflows, and video consultation integrations."],
  ["🧬","Chronic disease programs","Configure dedicated pathways for diabetes, hypertension and long-term conditions."],
  ["👨‍👩‍👧","Caregiver access","Consent-governed family participation and meaningful updates."],
  ["👶","Maternal health","Optional pathways for antenatal, newborn and postnatal monitoring."],
  ["🏥","Mobile clinic operations","Support outreach teams, field screenings and physical-to-virtual continuity of care."],
  ["🔐","Tenant and data governance","Separate customer organizations, permission profiles and auditable access processes."],
  ["🌍","Global operations","Local currencies, time zones and deployment regions subject to actual infrastructure."],
  ["✨","Clinician-reviewed AI","Future clinical summaries and administrative assistance with human oversight."]
];
let currentPage="overview";
const $ = id=>document.getElementById(id);
const tenant=()=>tenants[$("tenant").value];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function openModal(title,description){
 $("modal-title").textContent=title; $("modal-body").textContent=description; $("modal").classList.remove("hidden"); $("close").focus();
}
function closeModal(){ $("modal").classList.add("hidden"); }
function pill(status){let cl=status==="Alert"?"high":status==="Review"?"warn":"";return '<span class="pill '+cl+'">'+esc(status)+'</span>';}
function patientTable(t,limit){
 let p=Number.isInteger(limit)?t.patients.slice(0,limit):t.patients;
 return '<div class="tablewrap"><table class="data"><thead><tr><th>Patient (fictional)</th><th>Care program</th><th>Status</th><th>Last reading</th><th></th></tr></thead><tbody>'+p.map((x,i)=>'<tr><td><b>'+esc(x[0])+'</b><div class="caption">Synthetic record '+String(i+1).padStart(3,"0")+'</div></td><td>'+esc(x[1])+'</td><td>'+pill(x[2])+'</td><td>'+esc(x[4])+'<div class="caption">'+esc(x[3])+'</div></td><td><button class="textbtn" data-patient="'+i+'">Details →</button></td></tr>').join("")+'</tbody></table></div>';
}
function overview(t){
 const p=t.patients.length,n=t.observations.reduce((a,b)=>a+b,0);
 const rows=[["Diabetes care",t.patients.filter(x=>x[1].includes("Diabetes")).length],["Hypertension",t.patients.filter(x=>x[1].includes("Hypertension")).length],["Post-discharge & other",t.patients.filter(x=>!x[1].includes("Diabetes")&&!x[1].includes("Hypertension")).length]];
 const max=Math.max(...t.observations);
 return '<div class="grid kpis">'+[["Enrolled patients",p,"Synthetic cohort only"],["Observations",n,"Illustrative data points"],["Open alerts",t.alerts,"No real clinical triage"],["Care-team members",t.users,"Fictional staff"]].map(x=>'<div class="card"><div class="caption">'+x[0]+'</div><div class="metric">'+x[1]+'</div><div class="caption">'+x[2]+'</div></div>').join("")+'</div><div class="grid dash"><div class="card"><h3>Care activity · illustrative trend</h3><div class="spark" aria-label="Twelve synthetic activity bars">'+t.observations.map(v=>'<i style="height:'+Math.round(v/max*100)+'%"></i>').join("")+'</div><p class="caption">12-month example · not real clinical performance data</p></div><div class="card"><h3>Care programs</h3>'+rows.map(x=>'<div class="line"><span>'+esc(x[0])+'</span><div class="bar"><i style="width:'+Math.round(x[1]/Math.max(1,p)*100)+'%"></i></div><b>'+x[1]+'</b></div>').join("")+'</div></div><div class="card" style="margin-top:17px"><div class="line"><h3 style="margin:0">Recently monitored patients</h3><button class="textbtn" data-goto="patients">View all →</button></div>'+patientTable(t,3)+'</div>';
}
function patients(t){return '<div class="card"><h3>Patient workspace · '+esc(t.name)+'</h3>'+patientTable(t)+'</div>';}
function monitoring(t){return '<div class="grid two"><div class="card"><h3>Monitoring stream</h3><p class="sub">Representative observations from fictional records. No medical device is connected.</p>'+t.patients.map(x=>'<div class="line"><div><b>'+esc(x[0])+'</b><div class="caption">'+esc(x[1])+'</div></div><div style="text-align:right"><b>'+esc(x[4])+'</b><div class="caption">'+esc(x[3])+'</div></div></div>').join("")+'</div><div class="card"><h3>Clinical workflow design</h3><p class="sub">Proposed future escalation: device signal → normalization → consent verification → configured clinical rule → clinician acknowledgment → documented action.</p><div class="notice">AI recommendations and autonomous clinical decisions are not implemented in this demo.</div><button class="cta" data-modal="workflow">Review sample workflow</button></div></div>';}
function services(){return '<div class="grid modules">'+modules.map((m,i)=>'<div class="card module"><div class="emoji">'+m[0]+'</div><h3>'+esc(m[1])+'</h3><p>'+esc(m[2])+'</p><button class="textbtn" data-module="'+i+'">View proposed capability →</button></div>').join("")+'</div>';}
function plans(t){const cc=t.currency==="CAD"?"CAD":"USD";return '<p class="sub">Illustrative institutional subscriptions in '+cc+'. These are not offers for regulated medical services or payment-ready subscriptions.</p><div class="grid prices">'+[["Starter","99","25","Small practice"],["Professional","299","100","Growing clinic"],["Business","799","300","Multi-site organization"],["Enterprise","Custom","Custom","Hospital / insurer"]].map((p,i)=>'<div class="card plan '+(i===1?"pop":"")+'"><h3>'+p[0]+'</h3><div class="price">'+(p[1]==="Custom"?"Contact sales":cc+" "+p[1])+'</div><p>'+p[3]+'</p><ul><li>Up to '+p[2]+' monitored patients</li><li>Tenant-scoped workspaces</li><li>Proposed care-team workflows</li><li>Implementation subject to readiness</li></ul><button class="cta" data-plan="'+i+'">Discuss plan →</button></div>').join("")+'</div>';}
function render(page){
 currentPage=page;const t=tenant();
 document.querySelectorAll("[data-page]").forEach(b=>b.classList.toggle("active",b.dataset.page===page));
 const names={overview:["Overview","Connected care, clearly delivered.","One intelligent operating environment for modern healthcare organizations."],patients:["Patients","Every person. One coordinated view.","Track fictional patient enrollment and care programs within the selected organization."],monitor:["Monitoring","From readings to responsible action.","A proposed clinician-led model for observing, reviewing and escalating care."],modules:["Services","One platform, multiple care models.","Composable products for providers, partners and care teams."],plans:["Subscriptions","Healthcare as a service, built to scale.","Illustrative recurring subscriptions for independent healthcare organizations."]};
 const n=names[page]; $("crumb").textContent=n[0];$("title").textContent=n[1];$("subtitle").textContent=n[2];
 $("body").innerHTML=page==="overview"?overview(t):page==="patients"?patients(t):page==="monitor"?monitoring(t):page==="modules"?services():plans(t);
}
document.querySelector(".nav").addEventListener("click",e=>{const b=e.target.closest("[data-page]");if(b)render(b.dataset.page);});
document.body.addEventListener("click",e=>{
 const b=e.target.closest("[data-patient],[data-goto],[data-module],[data-plan],[data-modal]");
 if(!b)return;
 if(b.dataset.goto){render(b.dataset.goto);return;}
 if(b.dataset.patient!==undefined){let p=tenant().patients[Number(b.dataset.patient)];if(p)openModal(p[0]+" · synthetic record","Condition: "+p[1]+". Current status: "+p[2]+". Example reading: "+p[4]+". Last updated: "+p[3]+". This demonstration does not contain real patient information.");}
 if(b.dataset.module!==undefined){let m=modules[Number(b.dataset.module)];openModal(m[1],m[2]+" This capability is planned or illustrative and is not clinically certified.");}
 if(b.dataset.plan!==undefined){openModal("Commercial subscription inquiry","This is illustrative pricing only. Billing and customer onboarding are not enabled. Learn more through OECS Trading: https://oecstrading.com/");}
 if(b.dataset.modal){openModal("Illustrative escalation","A properly governed implementation would use validated source measurements, patient consent, configured thresholds approved by clinicians, an accountable care-team queue, and documented clinical follow-up.");}
});
$("tenant").addEventListener("change",()=>render(currentPage));
$("contact").addEventListener("click",()=>openModal("Explore XelaCare HaaS","XelaCare is in engineering development and is not accepting real patient data. To discuss an institutional pilot, contact OECS Trading via https://oecstrading.com/"));
$("close").addEventListener("click",closeModal);
$("modal").addEventListener("click",e=>{if(e.target===$("modal"))closeModal();});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal();});
render("overview");
