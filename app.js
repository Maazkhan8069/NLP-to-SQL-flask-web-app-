$(document).ready(function () {
    $("#conversion-form").submit(function (e) {
        e.preventDefault(); // Prevent the default form submission

        // Get the form data
        const formData = new FormData(this);

        // Make a POST request to the Flask backend
        $.ajax({
            type: "POST",
            url: "/convert",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                // Update the table headers (column names)
                $("#columns-row").empty();
                for (const column in response.results[0]) {
                    $("#columns-row").append(`<th>${column}</th>`);
                }

                // Update the table body (results)
                $("#results-body").empty();
                for (const row of response.results) {
                    let htmlRow = "<tr>";
                    for (const column in row) {
                        htmlRow += `<td>${row[column]}</td>`;
                    }
                    htmlRow += "</tr>";
                    $("#results-body").append(htmlRow);
                }
            },
            error: function (error) {
                console.error("Error occurred during conversion:", error);
                $("#columns-row").empty();
                $("#results-body").empty();
            },
        });
    });
});
