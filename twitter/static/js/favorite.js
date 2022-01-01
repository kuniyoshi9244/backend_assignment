$(document).on('click', '.favor_tweet', function(e){
  $.ajax({
    type : "POST",
    url: url_register_favorite_tweet,
    data: {'tweet_pk': $(e.target).val()},
    datatype: 'json',
    success: function(){
      $(e.target).replaceWith('<button class="delete_favorite_tweet  btn btn-danger btn-sm" value='+ $(e.target).attr('value') +'>お気に入り登録済み</button>')
    },
    error: function(){
      alert('登録に失敗しました。');
    }
  });
});

$(document).on('click', '.delete_favorite_tweet', function(e){
  $.ajax({
    type : "POST",
    url: url_delete_favorite_tweet,
    data: {'tweet_pk': $(e.target).val()},
    datatype: 'json',
    success: function(){
      $(e.target).replaceWith('<button class="favor_tweet  btn btn-primary btn-sm" value='+ $(e.target).attr('value') +'>お気に入り登録</button>')
    },
    error: function(){
      alert('登録に失敗しました。');
    }
  });
});