async function loadListeners() {
    //table listeners
    var countries = document.getElementsByClassName("list__country")
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

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};

function changeURLCountry(country){
    window.location.href = 'http://localhost:8000/country?name=' + country
}

loadListeners()
const values = ['inflation', 'pib']
values.forEach(v => {
    const data = Array.from(document.getElementsByClassName(v)).filter(i => i.textContent).sort((a,b) => Number(a.textContent) - Number(b.textContent))
    const rainbow = new Rainbow()
    rainbow.setSpectrum('red', 'green');
    rainbow.setNumberRange(0, data.length - 1);
    
    data.forEach((i, index) => {
        i.style.backgroundColor = '#' + rainbow.colorAt(index)
    })
})

Array.from(document.getElementsByClassName('paginator--page')).forEach(p => {
    const order = getUrlParameter('order')
    p.onclick = () => {
        document.location.href = 'http://localhost:8000/landing?page=' + p.innerHTML + (order ? '&order=' + order : '')
    }
})
console.log(getUrlParameter('page'))