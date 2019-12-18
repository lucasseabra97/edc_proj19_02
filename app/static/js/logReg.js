const Http = new XMLHttpRequest();
/* const url='https://jsonplaceholder.typicode.com/posts';
Http.open("GET", url);
Http.send();

Http.onreadystatechange = (e) => {
  console.log(Http.responseText)
} */

document.getElementById('form').addEventListener('submit', (e) => {
  e.preventDefault()
})
document.getElementById('register').addEventListener('click', (e) => {
  if(document.getElementById('form').checkValidity()) {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    $.ajax({
      url: 'http://localhost:8000/register',
      type: 'post',
      data: {'user' : username, 'pass': password},
      success: (res) => {
        Cookies.set('username', username)
        Cookies.set('password', password)
        window.location.href = 'http://localhost:8000/landing'
      },
      error: (err) => {
        alert('Username já em uso!')
      }
    })

  }
})
document.getElementById('login').addEventListener('click', (e) => {
  if(document.getElementById('form').checkValidity()) {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    $.ajax({
      url: 'http://localhost:8000/login',
      type: 'post',
      data: {'user' : username, 'pass': password},
      success: (res) => {
        Cookies.set('username', username)
        Cookies.set('password', password)
        window.location.href = 'http://localhost:8000/landing'
      },
      error: (err) => {
        alert('Username ou password errada!')
      }
    })

  }
})