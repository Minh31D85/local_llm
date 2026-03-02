document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("prompt");
    const generateBtn = document.getElementById("generateBtn");

    if(input){
        input.addEventListener("keydown", (e) => {
            if(e.key === "Enter" && !e.shiftKey && !e.repeat){
                e.preventDefault();
                generate();
            }
        })
    }
    if(generateBtn){
        generateBtn.addEventListener("click", generate);
    }
})


async function generate() {
    const promptField = document.getElementById("prompt");
    const prompt = promptField?.value || "";
    const language = document.getElementById("language")?.value || "python";
    const loader = document.getElementById("loader");
    const output = document.getElementById("output");

    if(!prompt.trim()){
        alert("Prompt required");
        return;
    }

    if(loader) loader.style.display = "block";
    if(output) output.textContent = "";

    try{
        const response = await fetch("/api/code/generate/", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt, language })
        });
        if(!response.ok) throw new Error("Server error: " + response.status);

        const data = await response.json();

        if(output){
            output.textContent = data.error 
            ? "Error: " + data.error 
            : data.code;
            if(promptField) promptField.value = "";
        }
    }catch(err){
        if(output) output.textContent = "Connection error";
    }finally{
        if(loader) loader.style.display = "none"; 
    }
}