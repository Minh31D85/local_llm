document.addEventListener("DOMContentLoaded", () => {
    const ui = getUI();

    if(ui.prompt){
            ui.prompt.addEventListener("keydown", (e) => {
                if(e.key === "Enter" && !e.shiftKey && !e.repeat){
                    e.preventDefault();
                    generate();
                }
            })
        }

    if(ui.generateBtn){ 
        ui.generateBtn.addEventListener("click", generate);
    }

    if(ui.prompt && ui.clearBtn){
        const toggleVisibility = () => {
            ui.clearBtn.style.opacity = ui.prompt.value.trim() ? "1" : "0";
        }
        ui.prompt.addEventListener("input", toggleVisibility);

        ui.clearBtn.addEventListener("click", () => {
            ui.prompt.value = "";
            ui.prompt.focus();
            toggleVisibility();
        })
        toggleVisibility();
    }
    loadHistory();
})


async function generate() {
    const ui = getUI();

    const prompt = ui.prompt.value.trim();
    if(!prompt){ 
        alert("Prompt required"); 
        return; 
    }

    resetOutput(ui);
    startTimer(ui.loader);

    let fullText = "";

    try{
        const response = await fetch("/api/code/generate/", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });

        if(!response.ok){
            ui.codeElement.textContent = "Server error";
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while(true){
            const {done, value} = await reader.read();
            if(done) break;

            const chunk = decoder.decode(value, {stream: true});

            fullText += chunk;

            appendChunk(ui.codeElement, chunk);

            tokenCount += countToken(chunk);
        }   

        const parsed = parseLLMRes(fullText);

        ui.analysisElement.innerHTML = marked.parse(parsed.analysis)

        applyLanguage(ui.codeElement, parsed.lang);

        ui.codeElement.textContent = parsed.code;

        Prism.highlightElement(ui.codeElement);

        ui.prompt.value = "";

        await new Promise(resolve => setTimeout(resolve, 400));
        await loadHistory();
    }catch(err){
        if(ui.codeElement) ui.codeElement.textContent = "Connection error";
    }finally{
        stopTimer(ui.loader);
        if(ui.generateBtn) ui.generateBtn.disabled = false;
    }
}


function appendChunk(el, chunk){
    el.textContent += chunk;
}


function countToken(text){
    return text.trim().split(/\s+/).filter(Boolean).length;
}


function getUI(){
    return {
        prompt: document.getElementById("prompt"),
        loader: document.getElementById("loader"),
        codeElement:document.getElementById("output-code"),
        generateBtn:document.getElementById("generateBtn"),
        analysisElement:document.getElementById("analysis"),
        clearBtn: document.getElementById("clearBtn")

    }  
}


function resetOutput(ui){
    tokenCount = 0;
    ui.codeElement.textContent = "";
    ui.analysisElement.innerHTML = "";

    ui.loader.style.display = "block";
    ui.generateBtn.disabled = true;
}


async function loadHistory() {
    
    const container = document.getElementById("history");
    if(!container) return;
    
    const response = await fetch("/api/code/history/");
    const data =  await response.json();
console.log("History loaded", data);
    container.innerHTML = "";

    data.forEach(entry => {
        const div = document.createElement("div");
        div.className = "history-item";

        const text = document.createElement("span");
        text.className = "history-text";
        text.textContent = entry.prompt.substring(0, 40);

        const delBtn = document.createElement("button");
        delBtn.className = "history-delete";
        delBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="14" height="14">
            <path d="M6 6 L18 18 M18 6 L6 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"/>
        </svg>
        `;

        delBtn.onclick = async () => {
            await deleteEntry(entry.id);
            loadHistory();
        };

        div.appendChild(text);
        div.appendChild(delBtn);

        div.onclick = (e) => {
            if(e.target === delBtn) return;
            const promptField = document.getElementById("prompt");
            const outputField = document.getElementById("output-code");

            if(promptField)promptField.value = entry.prompt;
            if(outputField){
                outputField.textContent = entry.response;
                Prism.highlightElement(outputField);
            }
        }
        container.appendChild(div);
    })
}



async function deleteEntry(id) {
    try{
        const response = await fetch(`/api/code/history/${id}/`, {
            method: "DELETE"
        });
        if(!response.ok){
            console.error("Delete failed");
            alert("Delete failed");
        }    
    }catch(err){
        console.error("Connection error")
    }
}



let timerInterval = null;
let tokenCount = 0;

function startTimer(loader){
    const startTime = Date.now();

    timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        loader.textContent = `Generating.. ${elapsed.toFixed(1)}s | tokens: ${tokenCount}`;
    }, 100);
}


function stopTimer(loader){
    if(timerInterval){
        clearInterval(timerInterval);
        timerInterval = null;
    }
    loader.style.display = "none";
}


function parseLLMRes(text){
    const match = text.match(/```(\w+)?\n([\s\S]*?)```/);
    
    if(!match){
        return { 
            analysis: text, 
            code: "",
            lang: "plaintext"
        };
    }  

    const lang = match[1] || "plaintext";
    const code = match[2];
    
    const analysis = text.replace(match[0], "").trim();
    return { analysis, code, lang };
}


function applyLanguage(codeElement, lang){
    codeElement.className = "";
    codeElement.classList.add("language-" + lang);
}