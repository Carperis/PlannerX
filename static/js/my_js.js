$(document).ready(function () {
    adjustDivWidth()

    $("#report_form").hide();
    $("#survey_form").hide();

  // When the button is focused, show the content div
  $("#feedback_btn").on("click", function () {
    if ($("#feedback_form").hasClass("float_content_active")) {
      $("#feedback_form").removeClass("float_content_active");
    } else {
      $("#feedback_form").addClass("float_content_active");
    }
  });

  // When the button loses focus, hide the content div
  $("body").on("mousedown", function () {
    if (!$("#feedback_form").is(":hover") && !$("#feedback_btn").is(":hover")){
      $("#feedback_form").removeClass("float_content_active");
    }
  });

  $("#survey_btn").on("click", function () {
    $("#survey_form").show();
    $("#report_form").hide();
  });

  $("#report_btn").on("click", function () {
    $("#report_form").show();
    $("#survey_form").hide();
  });

  $(window).on("resize", function() {
    adjustDivWidth();
  });



});


function adjustDivWidth() {
    var ideaWidth = 500
    var windowWidth = $(window).width();
    var divWidth = windowWidth < ideaWidth ? windowWidth : ideaWidth;
    $("#feedback_box").css("width", divWidth + "px");
}
