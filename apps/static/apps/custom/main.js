jQuery(document).ready(function ($) {
    // Apply input mask for the phone number input field
    $('form > .input-group:first > input:first').inputmask({
        "mask": "+\\9\\98(99) 999-99-99"
    });

    $('#id_phone').inputmask({
        "mask": "+\\9\\98(99) 999-99-99"
    });
});
