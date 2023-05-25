
function textAdaptationEvent(event, alternativeText, tagIdentify, elemnt) {
  event.preventDefault();
  const container = document.querySelector(`.${tagIdentify}`);
  if(!localStorage.getItem(tagIdentify)){
    localStorage.setItem(tagIdentify, container.innerHTML)
  }
  let value = elemnt.classList.toggle("active");
  if (value) {
    elemnt.setAttribute("aria-label", "Lectura normal");
    container.innerHTML = alternativeText;
  } else {
    elemnt.setAttribute("aria-label", "Lectura facil");
    container.innerHTML = localStorage.getItem(tagIdentify);
    localStorage.removeItem(tagIdentify)
  }
}

function audioAdaptationEvent(event, audioSrc, tagIdentify, elemnt) {
  event.preventDefault();
  const container = document.querySelector(`.${tagIdentify}`);
  if(!localStorage.getItem(tagIdentify)){
    localStorage.setItem(tagIdentify, container.innerHTML)
  }
  let value = elemnt.classList.toggle("active");
  if (value) {
    elemnt.setAttribute("aria-label", "Convertir a texto");
    container.innerHTML = `<audio controls preload="none" src="${audioSrc}"></audio>`;
  } else {
    elemnt.setAttribute("aria-label", "Convertir a audio");
    container.innerHTML = localStorage.getItem(tagIdentify);
    localStorage.removeItem(tagIdentify);
  }
}
