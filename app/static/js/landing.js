async function loadListeners() {
    //table listeners
    var countries = document.getElementsByClassName("list__item")
    for(var c of countries){
        c.addEventListener('click', (event) => {
            changeURLCountry(event.target.parentElement.children[2].innerHTML)
        })
    }

    //sidebar listeners
    var pib = document.getElementById("pib")
    pib.addEventListener('click', () => {
        window.location.href = 'http://localhost:8000/pib'
    })

    var pib = document.getElementById("area")
    pib.addEventListener('click', () => {
        window.location.href = 'http://localhost:8000/area'
    })

    var pib = document.getElementById("populacao")
    pib.addEventListener('click', () => {
        window.location.href = 'http://localhost:8000/populacao'
    })

    var pib = document.getElementById("inflacao")
    pib.addEventListener('click', () => {
        window.location.href = 'http://localhost:8000/inflacao'
    })
}


function changeURLCountry(country){
    window.location.href = 'http://localhost:8000/country?name=' + country
}


loadListeners()