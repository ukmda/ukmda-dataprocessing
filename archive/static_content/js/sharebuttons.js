/* Additional code to handle share icons */
function MastodonShare(){
	src = window.location.href;
	domain = prompt("Enter your Mastodon domain", "mastodon.social");
	if (domain == "" || domain == null){
		return;
	}
	url = "https://" + domain + "/share?text=" + src;
	window.open(url, '_blank');
};

function FacebookShare(){
	src = window.location.href;
	url = "https://www.facebook.com/sharer/sharer.php?u=" + src;
	window.open(url, '_blank');
};

function TwitterShare(){
	src = window.location.href;
	url = "https://twitter.com/intent/tweet?text=&url=" + src;
	window.open(url, '_blank');
};
