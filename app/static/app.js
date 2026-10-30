document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const btnRunAgent = document.getElementById("btn-run-agent");
  const traceContainer = document.getElementById("trace-container");
  const traceCounter = document.getElementById("trace-counter");
  const courseSelect = document.getElementById("course-select");
  const recordingInput = document.getElementById("recording-input");

  // Tab elements
  const tabBtns = {
    audit: document.getElementById("tab-btn-audit"),
    commitments: document.getElementById("tab-btn-commitments"),
    package: document.getElementById("tab-btn-package"),
    chat: document.getElementById("tab-btn-chat"),
  };
  const tabContents = {
    audit: document.getElementById("tab-content-audit"),
    commitments: document.getElementById("tab-content-commitments"),
    package: document.getElementById("tab-content-package"),
    chat: document.getElementById("tab-content-chat"),
  };

  // Displays
  const classTitleDisplay = document.getElementById("class-title-display");
  const classDateDisplay = document.getElementById("class-date-display");
  const pacingStatusText = document.getElementById("pacing-status-text");
  const pacingBadge = document.getElementById("pacing-badge");
  const pacingExplanationText = document.getElementById("pacing-explanation-text");
  const pacingRecommendationText = document.getElementById("pacing-recommendation-text");
  const coveredTopicsList = document.getElementById("covered-topics-list");
  const pendingTopicsList = document.getElementById("pending-topics-list");
  const commitmentsContainer = document.getElementById("commitments-container");
  const packageTitle = document.getElementById("package-title");
  const packageObjective = document.getElementById("package-objective");
  const packageCode = document.getElementById("package-code");
  const btnCopyCode = document.getElementById("btn-copy-code");

  // Chat
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const btnSendChat = document.getElementById("btn-send-chat");

  // Switch tabs
  function switchTab(activeKey) {
    Object.keys(tabBtns).forEach((key) => {
      if (key === activeKey) {
        tabBtns[key].className = "px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white transition flex items-center gap-1.5 shadow";
        tabContents[key].classList.remove("hidden");
      } else {
        tabBtns[key].className = "px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";
        tabContents[key].classList.add("hidden");
      }
    });
  }

  Object.keys(tabBtns).forEach((key) => {
    tabBtns[key].addEventListener("click", () => switchTab(key));
  });

  // Run Agent
  btnRunAgent.addEventListener("click", async () => {
    btnRunAgent.disabled = true;
    btnRunAgent.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Razonando y Ejecutando Herramientas...</span>`;
    traceContainer.innerHTML = "";
    traceCounter.innerText = "Iniciando...";

    try {
      const res = await fetch("/api/agent/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          course_keyword: courseSelect.value,
          recording_id: recordingInput.value.trim()
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Render Traces sequentially with nice timing effect
      const traces = data.execution_trace || [];
      traceCounter.innerText = `${traces.length} Pasos Completados`;

      for (let i = 0; i < traces.length; i++) {
        const step = traces[i];
        const card = document.createElement("div");
        card.className = "step-card p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 text-xs space-y-2 shadow-md";
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-indigo-400 flex items-center gap-1.5">
              <span class="w-5 h-5 rounded-full bg-indigo-950 border border-indigo-700 flex items-center justify-center text-[10px] text-indigo-200">
                ${step.step_number}
              </span>
              Paso ${step.step_number}
            </span>
            <span class="px-2 py-0.5 rounded bg-slate-900 font-mono text-[10px] text-cyan-300 border border-slate-800">
              Tool: ${step.tool_name}
            </span>
          </div>
          <p class="text-slate-300 leading-relaxed font-sans">
            <strong class="text-slate-400">Thought:</strong> ${step.thought}
          </p>
          <div class="p-2 rounded-lg bg-slate-950/80 font-mono text-[11px] text-emerald-400 border border-slate-900/80">
            <span class="text-slate-500">Observation:</span> ${step.tool_output}
          </div>
        `;
        traceContainer.appendChild(card);
        traceContainer.scrollTop = traceContainer.scrollHeight;
        await new Promise((r) => setTimeout(r, 200));
      }

      // Update Audit UI
      if (data.audit_report) {
        const r = data.audit_report;
        classTitleDisplay.innerText = r.class_title;
        classDateDisplay.innerText = `Fecha: ${r.class_date}`;
        
        const pacing = r.pacing_diagnosis;
        pacingStatusText.innerText = pacing.pacing_status;
        pacingExplanationText.innerText = pacing.pacing_analysis;
        pacingRecommendationText.innerText = pacing.pedagogical_recommendation;

        if (pacing.pacing_status.toLowerCase().includes("behind")) {
          pacingBadge.className = "px-3.5 py-1.5 rounded-full text-xs font-bold bg-amber-950/80 border border-amber-600/60 text-amber-300 flex items-center gap-1.5 shadow-inner";
        } else {
          pacingBadge.className = "px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-950/80 border border-emerald-600/60 text-emerald-300 flex items-center gap-1.5 shadow-inner";
        }

        // Covered topics
        coveredTopicsList.innerHTML = "";
        (r.topics_covered || []).forEach((t) => {
          const item = document.createElement("div");
          item.className = "p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60";
          item.innerHTML = `<span class="font-semibold text-white">${t.topic}</span><p class="text-slate-400 mt-0.5">${t.key_takeaways}</p>`;
          coveredTopicsList.appendChild(item);
        });

        // Pending topics
        pendingTopicsList.innerHTML = "";
        (r.missing_or_delayed_topics || []).forEach((topic) => {
          const item = document.createElement("div");
          item.className = "p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/40 text-amber-200";
          item.innerText = `• ${topic}`;
          pendingTopicsList.appendChild(item);
        });

        // Commitments
        commitmentsContainer.innerHTML = "";
        (r.action_items || []).forEach((act) => {
          const item = document.createElement("div");
          const isCrit = act.priority === "Critical" || act.priority === "High";
          item.className = `p-3 rounded-xl border text-xs flex items-start justify-between ${
            isCrit ? "bg-red-950/20 border-red-800/40" : "bg-slate-800/60 border-slate-700/60"
          }`;
          item.innerHTML = `
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                  act.assignee === "Students" ? "bg-indigo-900 text-indigo-300" : "bg-cyan-900 text-cyan-300"
                }">${act.assignee}</span>
                <span class="text-slate-400 text-[11px] font-semibold">${act.category}</span>
              </div>
              <p class="text-slate-200 font-medium">${act.description}</p>
            </div>
            <div class="text-right pl-3 shrink-0">
              <span class="text-[10px] text-amber-400 font-mono">${act.deadline || "Próxima sesión"}</span>
            </div>
          `;
          commitmentsContainer.appendChild(item);
        });
      }

      // Update Next Class Package
      if (data.next_class_package) {
        const pkg = data.next_class_package;
        packageTitle.innerText = pkg.title;
        packageObjective.innerText = pkg.focus_objective;
        packageCode.innerText = pkg.demonstration_code;
      }

      switchTab("audit");

    } catch (err) {
      alert(`Error ejecutando agente: ${err.message}`);
    } finally {
      btnRunAgent.disabled = false;
      btnRunAgent.innerHTML = `<i class="fa-solid fa-brain"></i><span>Ejecutar Agente Autónomo</span>`;
    }
  });

  // Copy code button
  btnCopyCode.addEventListener("click", () => {
    navigator.clipboard.writeText(packageCode.innerText).then(() => {
      btnCopyCode.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> ¡Copiado!`;
      setTimeout(() => {
        btnCopyCode.innerHTML = `<i class="fa-regular fa-copy"></i> Copiar Código Demo`;
      }, 2000);
    });
  });

  // Chat handler
  async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";
    
    // Add user bubble
    const userMsg = document.createElement("div");
    userMsg.className = "p-3 rounded-xl bg-indigo-600/80 text-white ml-8 shadow-sm";
    userMsg.innerText = text;
    chatMessages.appendChild(userMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Loading indicator
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "p-3 rounded-xl bg-slate-800 text-slate-400 mr-8 flex items-center gap-2";
    loadingMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>El agente está pensando...</span>`;
    chatMessages.appendChild(loadingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      loadingMsg.remove();

      const botMsg = document.createElement("div");
      botMsg.className = "p-3 rounded-xl bg-slate-800/90 border border-slate-700 text-slate-200 mr-8 space-y-2";
      botMsg.innerHTML = data.reply.replace(/\n/g, "<br>");
      chatMessages.appendChild(botMsg);
      chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (e) {
      loadingMsg.innerHTML = `<span class="text-red-400">Error conectando con el agente.</span>`;
    }
  }

  btnSendChat.addEventListener("click", sendChatMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
});
