let navbar = document.querySelector('.navbar');
          document.querySelector('.menutoogle').onclick = () =>{
	        navbar.classList.toggle('active');
	        seacrhForm.classList.remove('active');

              }

          let seacrhForm = document.querySelector('.search-form');
          document.querySelector('.find').onclick = () =>{
	        seacrhForm.classList.toggle('active');

	        navbar.classList.remove('active');
              }

           let cartItem = document.querySelector('.Shop-items-container');
          document.querySelector('.shop').onclick = () =>{

	        navbar.classList.remove('active');
          	 seacrhForm.classList.remove('active');
              }
          window.onscroll = () =>{
          	navbar.classList.remove('active');
          	 seacrhForm.classList.remove('active');

          }