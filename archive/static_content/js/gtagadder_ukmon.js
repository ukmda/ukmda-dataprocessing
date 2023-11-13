// script to add google analytics tags
(function() {
    const head = document.getElementsByTagName("head")[0];
    var myScript = document.createElement('script');
    myScript.setAttribute('src', 'https://www.googletagmanager.com/gtag/js?id=G-D5710EJL12');
    myScript.onload = function() {
      window.dataLayer = window.dataLayer || [];
      function gtag() { dataLayer.push(arguments); }
      gtag('js', new Date());
      console.log('window.dataLayer Executed', window.dataLayer)
      gtag('config', 'G-D5710EJL12');
    }
    head.insertBefore(myScript, head.children[1]);
  })();
