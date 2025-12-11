const textInput = document.getElementById("textInput");
const imageFile = document.getElementById("imageFile");
const canvas = document.getElementById("previewCanvas");
const printBtn = document.getElementById("printBtn");
const receipt = document.getElementById("receipt");
const statusBox = document.getElementById("status");
//const nameInput = document.getElementById("name");
//const titleInput = document.getElementById("title");

// ---------------- IMAGE PREVIEW ----------------
imageFile.addEventListener("change", () => {
  const file = imageFile.files[0];
  if(!file){ canvas.width=0; return; }
  const img = new Image();
  img.src = URL.createObjectURL(file);
  img.onload = () => {
    const W = 384;
    const H = Math.round(img.height*(W/img.width));
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle="#fff";
    ctx.fillRect(0,0,W,H);
    ctx.drawImage(img,0,0,W,H);
  };
});

// ---------------- PRINT ----------------
printBtn.addEventListener("click", async () => {
  printBtn.disabled = true;
  statusBox.textContent = "sending…";
  statusBox.classList.remove("hidden");

  const form = new FormData();
  //form.set("name", nameInput.value.trim());
  //form.set("title", titleInput.value.trim());
  form.set("text", textInput.value);

  const hasImage = imageFile.files.length > 0;
  form.set("has_image", hasImage ? "true" : "false");
  
  // send canvas image as file
  if(canvas.width>0 && canvas.height>0){
    canvas.toBlob(blob => {
      form.append("image", blob, "preview.png");
      sendToPrinter(form);
    });
  } else {
    sendToPrinter(form);
  }

  // Jolty animation
  receipt.classList.add("jolt-up");
  setTimeout(()=>{ receipt.classList.remove("jolt-up"); }, 800);
});

async function sendToPrinter(form){
  try{
    const res = await fetch("/print", { method:"POST", body: form });
    const msg = await res.text();
    statusBox.textContent = msg;
  } catch(e){
    statusBox.textContent = "error sending to printer";
  }
  printBtn.disabled=false;
}
