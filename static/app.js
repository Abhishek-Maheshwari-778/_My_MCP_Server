document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const fileNameDisplay = document.getElementById("fileName");
  const browseBtn = document.getElementById("browseBtn");
  
  const configForm = document.getElementById("configForm");
  
  const runBtn = document.getElementById("runBtn");
  const sendEmailCheck = document.getElementById("sendEmailCheck");
  const statusBox = document.getElementById("statusBox");
  const statusText = document.getElementById("statusText");
  const progressFill = document.getElementById("progressFill");
  const resultsSection = document.getElementById("resultsSection");
  const domainSelect = document.getElementById("domainSelect");

  // Nav Elements
  const navAppBtn = document.getElementById("navAppBtn");
  const navAboutBtn = document.getElementById("navAboutBtn");
  const appView = document.getElementById("appView");
  const aboutView = document.getElementById("aboutView");

  let uploadedFilename = null;

  // Load saved config
  const savedConfig = JSON.parse(localStorage.getItem("aiAnalyticsConfig") || "{}");
  if(savedConfig.nvidiaKey) document.getElementById("nvidiaKey").value = savedConfig.nvidiaKey;
  if(savedConfig.groqKey) document.getElementById("groqKey").value = savedConfig.groqKey;
  if(savedConfig.deepseekKey) document.getElementById("deepseekKey").value = savedConfig.deepseekKey;
  if(savedConfig.emailSender) document.getElementById("emailSender").value = savedConfig.emailSender;
  if(savedConfig.emailPassword) document.getElementById("emailPassword").value = savedConfig.emailPassword;
  if(savedConfig.emailReceiver) document.getElementById("emailReceiver").value = savedConfig.emailReceiver;

  // --- Navigation Handling ---
  navAppBtn.addEventListener("click", () => {
    navAppBtn.classList.add("active");
    navAboutBtn.classList.remove("active");
    appView.style.display = "grid";
    aboutView.style.display = "none";
  });

  navAboutBtn.addEventListener("click", () => {
    navAboutBtn.classList.add("active");
    navAppBtn.classList.remove("active");
    aboutView.style.display = "grid";
    appView.style.display = "none";
  });

  // --- Upload Handling ---
  browseBtn.addEventListener("click", () => fileInput.click());
  
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });
  
  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });
  
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if(e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if(e.target.files.length) {
      handleFile(e.target.files[0]);
    }
  });

  async function handleFile(file) {
    fileNameDisplay.textContent = `Uploading ${file.name}...`;
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if(res.ok) {
        uploadedFilename = data.filename;
        fileNameDisplay.textContent = `✅ Ready: ${file.name}`;
      } else {
        fileNameDisplay.textContent = `❌ Error: ${data.error}`;
      }
    } catch(err) {
      fileNameDisplay.textContent = `❌ Upload failed.`;
    }
  }

  // --- Config Handling ---
  configForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const config = {
      nvidiaKey: document.getElementById("nvidiaKey").value,
      groqKey: document.getElementById("groqKey").value,
      deepseekKey: document.getElementById("deepseekKey").value,
      emailSender: document.getElementById("emailSender").value,
      emailPassword: document.getElementById("emailPassword").value,
      emailReceiver: document.getElementById("emailReceiver").value,
    };
    
    localStorage.setItem("aiAnalyticsConfig", JSON.stringify(config));

    const formData = new FormData();
    formData.append("nvidia_key", config.nvidiaKey);
    formData.append("groq_key", config.groqKey);
    formData.append("deepseek_key", config.deepseekKey);
    formData.append("email_sender", config.emailSender);
    formData.append("email_password", config.emailPassword);
    formData.append("email_receiver", config.emailReceiver);

    try {
      const btn = configForm.querySelector("button");
      btn.textContent = "Saving...";
      await fetch("/api/settings", { method: "POST", body: formData });
      btn.textContent = "✅ Saved!";
      setTimeout(() => btn.textContent = "Save Settings", 2000);
    } catch(err) {
      alert("Failed to save settings to server.");
    }
  });

  // --- Run Pipeline ---
  runBtn.addEventListener("click", async () => {
    if(!uploadedFilename) {
      alert("Please upload a file first!");
      return;
    }

    // UI Updates
    runBtn.disabled = true;
    runBtn.querySelector(".btn-text").style.display = "none";
    runBtn.querySelector(".loader").style.display = "inline-block";
    statusBox.style.display = "block";
    resultsSection.style.display = "none";
    
    // Fake progress animation
    progressFill.style.width = "0%";
    statusText.textContent = "1/4: Cleaning Data & Removing Nulls...";
    setTimeout(() => { progressFill.style.width = "25%"; statusText.textContent = "2/4: Generating AI Insights (Llama 3 / DeepSeek)..."; }, 3000);
    setTimeout(() => { progressFill.style.width = "60%"; statusText.textContent = "3/4: Creating HTML Dashboard..."; }, 8000);
    setTimeout(() => { progressFill.style.width = "85%"; statusText.textContent = "4/4: Exporting PDF & PBI Files..."; }, 12000);

    const formData = new FormData();
    formData.append("filename", uploadedFilename);
    formData.append("domain", domainSelect.value);
    formData.append("send_email", sendEmailCheck.checked);

    try {
      const res = await fetch("/api/run", { method: "POST", body: formData });
      const data = await res.json();
      
      progressFill.style.width = "100%";
      statusText.textContent = "✅ Complete!";
      
      if(res.ok) {
        resultsSection.style.display = "block";
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
      } else {
        alert("Pipeline Error: " + data.error);
      }
    } catch(err) {
      alert("Failed to run pipeline.");
    } finally {
      runBtn.disabled = false;
      runBtn.querySelector(".btn-text").style.display = "inline";
      runBtn.querySelector(".loader").style.display = "none";
    }
  });
});
