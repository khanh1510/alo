const showMenu = (toggleId, navId) =>{
    const toggle = document.getElementById(toggleId),
          nav = document.getElementById(navId)
 
    toggle.addEventListener('click', () =>{
        // Add show-menu class to nav menu
        nav.classList.toggle('show-menu')
 
        // Add show-icon to show and hide the menu icon
        toggle.classList.toggle('show-icon')
    })
 }
 
 showMenu('nav-toggle','nav-menu')

/*=============== SHOW MENU ===============*/

// Ngăn ngừa việc nhập các ký tự không phải số


const searchInput = document.getElementById('search-input');

searchInput.addEventListener('keyup', (event) => {
  const query = event.target.value;

  // Truy vấn dữ liệu từ Firebase
  firebase.database().ref('your_data_path').orderByChild('name').equalTo(query).once('value', (snapshot) => {
    // Xử lý kết quả truy vấn
    const results = snapshot.val();

    // Hiển thị kết quả lên giao diện
    // ...
  });
});
