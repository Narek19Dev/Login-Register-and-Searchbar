const product = [
    {
        id: 0,
        image: 'https://www.spark.co.nz/content/dam/spark/images/product-images/devices/phones/samsung/s25-series/s25-ultra/titanium-white-silver/s25-ultra-titanium-white-silver-1.png',
        title: 'Samsung S25 Ulrta',
        price: 230
    },
    {
        id: 1,
        image: 'https://m.media-amazon.com/images/I/61mSUSY4xWL.jpg',
        title: 'Z Flip Foldable Mobile',
        price: 120
    },
    {
        id: 2,
        image: 'https://eldorado.am/media/catalog/product/cache/b636eac9f5e866652b5cbe8cee86d97c/a/p/apple_airpods_pro_2.jpg',
        title: 'Air Pods Pro',
        price: 60
    },
    {
        id: 3,
        image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShM0mongkREBu-5ZfXTXtvaWoet1TqUgMwRQ&s',
        title: 'Fifine A8 Microphone',
        price: 70
    },
    {
        id: 4,
        image: 'https://m.media-amazon.com/images/I/71LP40TtRHL.jpg',
        title: 'Fifine Headphones',
        price: 32
    },
    {
        id: 5,
        image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTsp5H0rQo5h1OlHaFOD5g0gIpxhNpP_N7YIQ&s',
        title: 'Iphone 16 Pro Max',
        price: 1.271
    },
    {
        id: 6,
        image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQe4jGvmx8uz9a_zwtmFZnX3Nv7lzmZWR1Z9g&s',
        title: 'Kvartal RP',
        price: 5
    },
]
const categories = [...new Set(product.map((item) => { return item }))]

document.getElementById('searchBar').addEventListener('keyup', (e) => {
    const searchData = e.target.value.toLowerCase();
    const filterData = categories.filter((item) => {
        return (
            item.title.toLowerCase().includes(searchData)
        )
    })
    displayItem(filterData)
});

const displayItem = (items)=> {
    document.getElementById('root').innerHTML=items.map((item)=>{
        var {image, title, price} = item;
        return(
            `<div class='box'>
                <div class='img-box'>
                    <img class='images' src=${image}></img>
                </div>
                <div class='bottom'>
                    <p>${title}</p>
                    <h2>$ ${price}.00</h2>
                    <button class="buy">Add to cart</button>
                </div>
            </div>`
        )
    }).join('')
};
displayItem(categories);

function showSidebar() {
  const sidebar = document.querySelector('.sidebar')
  sidebar.style.display = 'flex'
}
function hideSidebar() {
  const sidebar = document.querySelector('.sidebar')
  sidebar.style.display = 'none'
}