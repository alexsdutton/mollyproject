$(contactMoreLink);

function contactMoreLink() {
  $('.contact-pagination-controls-bottom').html(
    $('<a href="#" class="contact-pagination-more">More</a>').bind('click', contactMore)
  );
}

function contactMore(e) {
alert(e);
try { 
    pageNumber += 1;
    loc = window.location;
    url = loc.protocol + '//' + loc.host + loc.pathname + '?format=update&' + queryString + '&page=' + pageNumber;
    $('.contact-pagination-controls-bottom').html('<img src="'+media_url+'base/gif/loading.gif"/>');
    $.getJSON(url, function(data) {
      for (i in data.people) {
        person = $(data.people[i]).slideUp(0);
        if (i == 0)
          person.addClass('page-start');
        $('#contact-people').append(person);
      };
      if (data.page_number == data.page_count) {
        $('.contact-pagination-controls-bottom').remove();
        $('#contact-people').addClass('last');
      } else
        contactMoreLink()
        
    });
    } catch (e) {
    alert(e);
    }
    return false;

}
