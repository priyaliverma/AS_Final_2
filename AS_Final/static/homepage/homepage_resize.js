
		// resize container to size of background_image to allow for scrolling 
		// mostly for mobile browser support since position:fixed for background
		// leads to strange sizing
		
		// resize container to size of background_image to allow for scrolling 
		// mostly for mobile browser support since position:fixed for background
		// leads to strange sizing
		
		// intialize function
		// console.log("I'm in the script");
		go();

		window.addEventListener('resize', go);

		function go(){
	      background_image = document.getElementById("bg_img");
	      container = document.getElementById("container"); 
	      container.style.height = background_image.height;
	      // console.log(container.style.height);
		};
		
	