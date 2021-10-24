$(document).on('click', '.follow', function(e){
  $.ajax({
    type : "POST",
    url: url_follow,
    data: {'followee_pk': $(e.target).val()},
    datatype: 'json',
    success: function(){
      $(e.target).replaceWith('<button class="delete_follow  btn btn-danger btn-sm" value='+ $(e.target).attr('value') +'>フォロー解除</button>')
    },
    error: function(){
      alert('登録に失敗しました。');
    }
  });
});

$(document).on('click', '.delete_follow', function(e){
  $.ajax({
    type : "POST",
    url: url_delete_follow,
    data: {'followee_pk': $(e.target).val()},
    datatype: 'json',
    success: function(){
      $(e.target).replaceWith('<button class="follow  btn btn-primary btn-sm" value='+ $(e.target).attr('value') +'>フォローする</button>')
    },
    error: function(){
      alert('解除に失敗しました。');
    }
  });
});