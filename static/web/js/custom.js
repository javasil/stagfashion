function openCart() { document.getElementById("Cart").style.display = "block"; }
function closeCart() { document.getElementById("Cart").style.display = "none"; }
function openSearch() { document.getElementById("Search").style.display = "block"; }
function closeSearch() { document.getElementById("Search").style.display = "none"; }
function openSidemenu() { document.getElementById("Sidemenu").style.display = "block"; }
function closeSidemenu() { document.getElementById("Sidemenu").style.display = "none"; }

// after 5 sec, fade #navigator slowly
$(document).ready(function () {
    setTimeout(function () {
        $('#navigator').fadeOut(4000);
    }, 1000);
});

$(document).on("click", ".cartitem_rmvbutton", function (e) {
    e.preventDefault();
    $this = $(this);
    var url = $this.attr("data-url");
    var csrf_token = $("input[name='csrfmiddlewaretoken']").val();

    $.ajax({
        // send ajax request to url with csrf token
        url: url,
        type: "POST",
        data: { csrfmiddlewaretoken: csrf_token },
        success: function (response) {
            console.log(response);
            $this.closest(".item_parent").remove();
            Snackbar.show({
                text: response.message,
                pos: 'bottom-left',
                showAction: true,
                actionText: "Dismiss",
                duration: 6000,
                textColor: '#fff',
                backgroundColor: '#151515'
            });
            $("#totalValue").text(response.data.order_total);
            $("#totalItems").text(response.data.order_items_count);
        },
        error: function (response) {
            location.reload();
        }

    });
});