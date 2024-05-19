$(document).ready(function () {
  $("#check").click(function () {
    //  alert($(this).is(':checked'));
    $(this).is(":checked")? $("#password").attr("type", "text"): $("#password").attr("type", "password");
  });
  $("#confirmPassword").keyup(function () {
    var password = $("#password").val();
    var confirmPassword = $(this).val();

    if (password != confirmPassword) {
      $("#passwordMatchMessage")
        .text("Passwords do not match")
        .css("color", "red");
      $(".submit").prop("disabled", true);
    } else {
      $("#passwordMatchMessage")
        .text("Passwords match")
        .css("color", "green");
      if (password.length < 8) {
        $("#passwordMatchMessage")
          .text("Password length should be at least 8 characters")
          .css("color", "red");
        $(".submit").prop("disabled", true);
      } else {
        $("#passwordMatchMessage").text("");
        $(".submit").prop("disabled", false);
      }
    }
  });
});