$(contactMoreLink);

function contactMoreLink() {
  $('.contact-pagination-controls-bottom').html(
    $('<a href="#" class="contact-pagination-more">More</a>').bind('click', contactMore)
  );
}

function contactMore(e) {
    pageNumber += 1;
    loc = window.location;
    url = loc.protocol + '//' + loc.host + loc.pathname + '?format=update&' + queryString + '&page=' + pageNumber;
    $('.contact-pagination-controls-bottom').html("Fetching&hellip;");
    $.getJSON(url, function(data) {
      for (i in data.people) {
        person = $(data.people[i]).slideUp(0);
        $('#contact-people').append(person);
      };
      if (data.page_number == data.page_count)
        $('.contact-pagination-controls-bottom').remove()
      else
        contactMoreLink()
        
    });
    return false;
}
