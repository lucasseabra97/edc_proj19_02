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

const searchInput = document.getElementById('headerSearch')
searchInput.value = getUrlParameter('search') || ''
searchInput.addEventListener('keydown', (event) => {
    const order = getUrlParameter('order')
    const dir = getUrlParameter('dir')
    if(event.code == 'Enter') {
        document.location.href = 'http://localhost:8000/landing?search=' + searchInput.value 
            + (order ? '&order=' + order : '')
            + (dir ? '&dir=' + dir : '')
    }
})

function onNote() {
    document.location.href = 'http://localhost:8000/addnote?note=' + this.document.getElementById('noteId').value
}

function sort(col) {
    const order = getUrlParameter('order')
    var colOrder = col.children[0].innerHTML.split(' ')[0]
    const search = getUrlParameter('search')
    const page = getUrlParameter('page')
    var dir = getUrlParameter('dir')
    dir = order == colOrder ? (dir == 'asc' ? 'desc' : 'asc') : 'asc'
    document.location.href = 'http://localhost:8000/landing?order=' + colOrder
        + (search ? '&search=' + search : '')
        + (page ? '&page=' + page : '')
        + (dir ? '&dir=' + dir : '')
}

if(document.getElementsByClassName('list')) {
    const order = getUrlParameter('order')
    const dir = getUrlParameter('dir')
    if(order) {
        const div = document.createElement('span')
        div.innerHTML = dir == 'asc' ? '&uarr;' : '&darr;'
        document.getElementById(order).append(div)
        document.getElementById(order).style.backgroundColor = 'green'
    }
}

if(document.getElementsByClassName('paginator--page')) {
    Array.from(document.getElementsByClassName('paginator--page')).forEach(p => {
        const order = getUrlParameter('order')
        const search = getUrlParameter('search')
        const dir = getUrlParameter('dir')
        p.onclick = () => {
            document.location.href = 'http://localhost:8000/landing?page=' + p.innerHTML 
                + (order ? '&order=' + order : '')
                + (search ? '&search =' + search : '')
                + (dir ? '&dir =' + dir : '')
        }
    })
}

const values = [['inflation', ['green', 'red']], ['pib', ['red', 'green']]]
values.forEach(v => {
    const data = Array.from(document.getElementsByClassName(v[0])).filter(i => i.textContent).sort((a,b) => Number(a.textContent) - Number(b.textContent))
    
    if(data.length > 1) {
        const rainbow = new Rainbow()
        rainbow.setSpectrum(v[1][0], v[1][1]);
        rainbow.setNumberRange(0, data.length - 1);
        
        data.forEach((i, index) => {
            i.style.backgroundColor = '#' + rainbow.colorAt(index)
        })
    } else {
        data.forEach((i, index) => {
            i.style.color = 'black'
        })
    }
})

if (!document.cookie.includes('username') && window.location.pathname != '/') {
    document.location.href = 'http://localhost:8000'
}