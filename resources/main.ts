import "./styles.css"
import "./theme-switcher"

// document.addEventListener("htmx:responseError", (event: Event) => {
//   const customEvent = event as CustomEvent<{ xhr: XMLHttpRequest }>
//   const errorMessage = customEvent.detail.xhr.responseText
//   const alert = document.getElementById("alert-error")
//   const alertContainer = document.querySelector("#alert-error div.alert span")
//
//   if (alert && alertContainer) {
//     alertContainer.innerHTML = errorMessage
//     alert.classList.remove("hidden")
//   }
// })