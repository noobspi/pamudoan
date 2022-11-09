$(function () {
    initialize();

    //annotation handling
    $(document).on("click", "#add-annotation", function (event) {
        event.preventDefault();
        newAnnotation().insertBefore("#annotations > #annotations-footer");
        reindexAnnotations();
    });

    $(document).on("click", ".remove-annotation", function(event) {
        event.preventDefault();
        $(this).closest(".annotation").remove();
        reindexAnnotations();
    })

    //form submission: convert all labels to JSON and send to server 
    $(document).on("click", "#form_submit", function(event) {
        event.preventDefault();
        let data = {
            docid: $("#docid").val(),
            annotations: []
        }

        $(".annotation").each(function (index) {
            let annotation = {
                category: $(this).find(".category").val(),
                startpage: $(this).find(".page-from").val(),
                endpage: $(this).find(".page-to").val()
            };
            data.annotations.push(annotation);
        });
        $("#jsondata").val(JSON.stringify(data));

        // validate form-data before submit
        if ($("#annotations-form")[0].reportValidity()) { 
            $("#annotations-form").submit(); 
        }

        // ajax not needed here...
        // $.ajax({
        //     url: "/save",
        //     type: "POST",
        //     contentType: "application/json",
        //     data: JSON.stringify(data)
        // }).done(function () {
        //     addAlert("Speichern erfolgreich");
        //     window.location.reload();
        // }).fail(function() {
        //     addAlert("Speichern fehlgeschlagen");
        // });
    })
});

function initialize() {
    newAnnotation(true).insertBefore("#annotations > #annotations-footer");
    reindexAnnotations();
    hideAlertsAfterTimeout();
}

function hideAlertsAfterTimeout() {
    setTimeout(function() {
        $("#msg-flash .alert").remove();
        $("#msg-flash").hide();
    }, 3000);
}

function newAnnotation(isFirst) {
    //create select based on "annotations_labels": data is defined in the html
    let select = $("<select />")
                    .addClass("form-select category")
                    .attr("name", "annotation[][category]")
                    .attr("required", true)
                    .attr("data-placeholder", "Kategorie wählen")
                    .attr("placeholder",      "Kategorie wählen")
                    .attr("aria-label", "Kategorie wählen");
    $(select).append($("<option />").attr("hidden", true).attr("selected", true).attr("disabled", true).attr("value", "").text(""));  // empty option as defaut to show the placeholder
    for (let g of annotation_labels) {
        let og = $("<optgroup />").attr("label", g[0]);
        for (let l of g[1]) {
            $(og).append($("<option />").attr("value", l.value).text(l.label));
        }
        $(select).append(og);
    }

    //create annotation
    let annotation = 
    $("<div />").addClass("annotation row p-2").attr("style", "margin-top: 7px; background-color: #eeeeee; border: 1px solid #555555; border-radius: 5px;").append(
        $("<div />").addClass("col-11 pb-1").append(select)
    ).append(
        $("<div />").addClass("w-100")).append(
        $("<div />").addClass("col-3").append(
            $("<input />")
                .addClass("form-control page-from")
                .attr("placeholder", "Von Seite")
                .attr("aria-label", "Seite von")
                .attr("name", "annotation[][startpage]")
                .attr("type", "number")
                .attr("min", "1")
                .attr("max", "999")
                .attr("step", "1")
                .attr("pattern", "\d+")
                .attr("required", true)
        )
    ).append(
        $("<div />").addClass("col-3").append(
            $("<input />")
                .addClass("form-control page-to")
                .attr("placeholder", "Bis Seite")
                .attr("aria-label", "Seite bis")
                .attr("name", "annotation[][endpage]")
                .attr("type", "number")
                .attr("min", "1")
                .attr("max", "999")
                .attr("step", "1")
                .attr("pattern", "\d+")
                .attr("required", true)
        )
    );

    if(!isFirst) {
        annotation.append(
            $("<div />").addClass("col-5")).append(
            $("<div />").addClass("col-1").append(
                $("<button />").addClass("btn btn-sm btn-outline-danger text-nowrap remove-annotation").attr("type", "button")
                .append(
                    $("<i />").addClass("fa fa-trash")
                ))
            );

    }  
    
    // make the category-select a searchable jquery-select2
    select.select2({    
        width: "100%", 
        allowClear: false
    });
    return annotation;
}

function reindexAnnotations() {
    $(".annotation").each(function (index) {
        $(this).find(".category").attr("name", `annotations[${index}][label]`);
        $(this).find(".page-from").attr("name", `annotations[${index}][startpage]`);
        $(this).find(".page-to").attr("name", `annotations[${index}][endpage]`);
    });
}

function addAlert(msg) {
    $("#msg-flash").append(
        $("<div />").addClass("alert alert-danger").attr("role", "alert").text(msg)
    );
    $("#msg-flash").show();
    hideAlertsAfterTimeout();
}