$(document).ready(function() {
	$("#search-form").submit(function(e) {
		e.preventDefault();
		search();
	});

	fixContent();

	$(window).resize(fixContent);
});

function search() {
	let query = $("#search").val().trim();
	let domain = $("#domain").val();
	if (query) {
		window.location.href = "/search?q=" + query + "&in=" + domain;
	}
}

function fixContent() {
	$(".main-content").css("margin-top", $("#navbar").css("height"));
}