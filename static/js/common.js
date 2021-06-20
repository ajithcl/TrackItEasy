$(document).ready(function () {
    // Page default settings for books.html
    defaultBookSettings();

    // Greeting in summary page
    elmt_greeting = document.getElementById('set-greetings')
    if (elmt_greeting != null){
        let time = new Date();
        let greeting="";
        time = time.getHours();
        if (time < 12) {
        greeting = "Good Morning ";
        } else if (time >= 12 && time < 15) {
        greeting = "Good Afternoon ";
        }
        else if (time >= 15 && time < 20) {
        greeting = "Good Evening"
        }
        else { greeting = "Greetings " }
        elmt_greeting.appendChild(document.createTextNode(greeting));
    }

    // Login form submision
    $(document).on('submit', '#login-form', function (e) {
        e.preventDefault();

        var formdata = $(this).serialize();
        $.ajax({
            url: '/checklogin',
            type: 'POST',
            data: formdata,
            success: function (res) {
                if (res == 'error') {
                    alert('Login failure');
                }
                else {
                    window.location.href = "/summary";
                };
            }
        });
    });

    // Logout
    $(document).on('click', '#logout-link', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/logout',
            type: 'GET',
            success: function (res) {
                if (res == "success") {
                    window.location.href = "/login";
                }
                else {
                    alert("Error while logging out!");
                }
            }
        })
    })

    // Registration form submission

    $(document).on("submit", "#register-form", function (e) {
        e.preventDefault();

        var formData = $(this).serialize();
        $.ajax({
            url: '/postregistration',
            type: 'POST',
            data: formData,
            success: function (res) {
                if (res == "success") {
                    showMsgCard("Account created successfully! Sign in to see your content.", 'register-form', 'afterbtn');
                }
                else {
                    showMsgCard("Account creation failed. Try with different username.", 'register-form', 'afterbtn');
                    setTimeout(MsgCardTimeOut, 5000);
                };
            }
        });
    });

    // Add new book from Books.html
    $(document).on("submit", "#bookentryform", function (e) {
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            url: '/savebook',
            type: 'POST',
            data: formData,
            success: function (result) {
                window.location.reload();
            }
        })
    });

    // Book table event
    //    $("tr").click(function(){
    //        alert("tr clicked");
    //    })
    booktablebody = document.getElementById("booktable");
    if (booktablebody != null){
         booktablebody.addEventListener('dblclick', function (e) {
            e.target.parentElement.setAttribute("style", "background-color:red;");
            if (confirm("Do you want to delete this book?")== true){
                //alert(e.target.parentElement.dataset.rowid);
                bookid = {"_id" : e.target.parentElement.dataset.rowid};
                $.ajax({
                    url: '/deletebook',
                    data: bookid,
                    type: 'POST',
                    success: function (result){
                        if (result == "success"){
                            window.location.reload();
                        }
                        else{
                            alert("Book didn't deleted.");
                            e.target.parentElement.setAttribute("style", "");
                        }
                    }
                })
            }
            else{
                e.target.parentElement.setAttribute("style", "");
            }
         });
    }

    // Learning save button
    $(document).on("click", "#btnsavelearning", function(e){
        e.preventDefault();
        subject = $("#subject").val();
        formData = {"Subject" : subject};
        $.ajax({
            url: '/savelearning',
            type: 'POST',
            data: formData,
            success : function (result){
                if (result == "success"){
                    alertElmt = document.createElement('div');
                    alertElmt.className="alert alert-success";
                    alertElmt.id="learningresultalert";
                    alertElmt.setAttribute("role", "alert");
                    alertElmt.appendChild(document.createTextNode("Subject saved."));
                    insideElmt = document.getElementById("learningentrydiv");
                    beforeElmt =  document.getElementById("AfterSaveplaceholder");
                    insideElmt.insertBefore(alertElmt, beforeElmt);
                    setTimeout(removeLearningMsg,2000);
                }
                else{
                    alertElmt = document.createElement('div');
                    alertElmt.className="alert alert-danger";
                    alertElmt.id="learningresultalert";
                    alertElmt.setAttribute("role", "alert");
                    alertElmt.appendChild(document.createTextNode("Subject didn't saved."));
                    insideElmt = document.getElementById("learningentrydiv");
                    beforeElmt =  document.getElementById("AfterSaveplaceholder");
                    insideElmt.insertBefore(alertElmt, beforeElmt);
                    setTimeout(removeLearningMsg,2000);
                }
            }
        })

    })

    //Reminders save form
    $(document).on("submit", "#form_reminder_input", function(e){
        var formData = $(this).serialize();
        $.ajax({
            url: '/savereminder',
            type : 'POST',
            data : formData,
            success : function (result){
                if (result != "success")
                    alert("Unable to save the record");
            }
        })
    })

    //Expense entry form save
    $(document).on("submit", "#expense_entry_form", function(e){
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            url: '/save_expense',
            type: 'POST',
            data: formData,
            success: function(result){
                if (result == "success"){
                    window.location.reload();
                }
                else{
                    alert("Unable to save expense");
                }
            }
        })
    })


    //Journal save button / submit form
    $(document).on("submit", "#journal-entry-form", function(e){
        e.preventDefault();
        var form_data = $(this).serialize();
        const div_element = document.createElement('div');
        const form_element = document.getElementById('journal-entry-form');
        const msg_space = document.getElementById('journal_msg_space');
        const save_btn = document.getElementById("btn_journal_Save");
        const cancel_btn = document.getElementById("btn_journal_cancel");
        const subj = document.getElementById("objectid_input");

        if (subj.value == ""){
            /* Create new record */
            $.ajax({
                url : '/createjournal',
                type : 'POST',
                data : form_data,
                success : function (result){
                    if (result == "success"){
                        div_element.className = "alert alert-success text-center";
                        div_element.appendChild(document.createTextNode("Notes saved."));
                        form_element.insertBefore(div_element, msg_space);
                        setTimeout(clearJournalMessage, 2000);

                        displayJournalRecord("","","","Save");
                    }
                    else{
                        div_element.className = "alert alert-error text-center";
                        div_element.appendChild(document.createTextNode("Unable to save notes"));
                        form_element.insertBefore(div_element, msg_space);
                        setTimeout(clearJournalMessage, 2000);
                    }
                }
            })
        }
        else {
            /* Updating existing record */
            $.ajax({
                url:'/updatejournal',
                data: form_data,
                type: 'POST',
                success: function(result){
                    if (result === "success"){
                        div_element.className = "alert alert-success text-center";
                        div_element.appendChild(document.createTextNode("Notes saved."));
                        form_element.insertBefore(div_element, msg_space);
                        setTimeout(clearJournalMessage, 2000);

                        displayJournalRecord("","","","Save");
                    }
                    else{
                        div_element.className = "alert alert-error text-center";
                        div_element.appendChild(document.createTextNode("Unable to save notes"));
                        form_element.insertBefore(div_element, msg_space);
                        setTimeout(clearJournalMessage, 2000);
                    }
                }
            })
        }
        // Reset the save button text
        save_btn.innerText = "Save";
    })

    // Click events for the Journal cards
    journal_body = document.getElementById('journal_cards');
    if (journal_body != null){
        journal_body.addEventListener('click', function(e){
            //e.target.parentElement.setAttribute('style', 'background-color:green;');
            journalCardClicked(e.target.parentElement.getAttribute("data-objectid"))

        });
        journal_body.addEventListener('mouseover', function(e){
            if(e.target.className == "card-header"){
                card_header = e.target;
                card_body = card_header.nextElementSibling;
                object_id = card_body.getAttribute("data-objectid");
                if (card_header.hasChildNodes() == true){
                    if (card_header.childNodes[1]){
                    }else{
                        e.target.innerHTML += '<img class="journal_del_icon" src="/static/Common/remove_icon.png" onclick="delete_jounal(object_id, card_header)" width="33" height="33">';
                    }
                }
            }
        })
        journal_body.addEventListener('mouseleave', function(e){
            del_icons = document.getElementsByClassName('journal_del_icon');
            while (del_icons.length > 0){
                del_icons[0].remove();
            }
        })
    }

    // Save button from Movies page
    $(document).on("submit", "#form_movie_input", function(e){
        e.preventDefault();
        language = document.getElementById('inputGroupSelectMovieLanguage');
        movie_type = document.getElementById('inputGroupSelectMovieType');
        if (language.selectedIndex == 0 || movie_type.selectedIndex == 0){
            showMoviesMessage("Invalid entry for Type/Language");
            setTimeout(clearMovieMessage,3000);
            return;
        }
        var formData = $(this).serialize();
        $.ajax({
            url: "/save_movie",
            type : 'POST',
            data : formData,
            success : function (result){
                if (result == "success"){
                    window.location.reload();
                }
                else{
                    showMoviesMessage("Unable to save movie record.");
                    setTimeout(clearMovieMessage,3000);
                }
            }
        })
    })
})

// Show Movies message
function showMoviesMessage(ipMessage){
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message text-danger';
    msgDiv.appendChild(document.createTextNode(ipMessage));
    const formElement = document.getElementById('form_movie_input');
    const btn_save = document.getElementById('btn_Movies_save');
    formElement.insertBefore(msgDiv, btn_save);
}

function clearMovieMessage(){
    document.querySelector('.message').remove();
}

// delete journal notes
function delete_jounal(object_id, card_header){
    const confirm_del = confirm("Do you want to delete notes?");
    if (confirm_del == true){
        $.ajax({
            url: '/delete_journal_one',
            type: 'POST',
            data : {"objectid": object_id},
            success: function (result){
                card_header.parentElement.remove();
            }
        }
        )
    }
}

//for showing message card
function showMsgCard(ipError, insideElement, insertBeforeElement) {
    const errDiv = document.createElement('div');
    errDiv.className = 'errorAlert text-warning';
    errDiv.appendChild(document.createTextNode(ipError));
    elmtInside = document.getElementById(insideElement);
    elmtBefore = document.getElementById(insertBeforeElement);
    elmtInside.insertBefore(errDiv, elmtBefore);
}

// for removing message card
function MsgCardTimeOut() {
    document.querySelector('.errorAlert').remove();
}

// From Books.html
function bookRowBtnClicked(bookid){
    $.ajax({
        url: '/getbookone',
        data: {"_id" : bookid},
        type: 'GET',
        success: function(result){
            displayBookInForm(result, bookid);
            document.getElementById("btnAddUpdate").innerText = "Update Book";
            document.getElementById("btnCancel").hidden = false;
        }
    })
}

function displayBookInForm(strInput, bookId){
    jsonData = JSON.parse(strInput);
    document.getElementById("BookName").value = jsonData.BookName;
    $('#RelatedTo').val(jsonData.RelatedTo);
    $('#Author').val(jsonData.Author);
    $("#Comments").val(jsonData.Comments);
    $("#StartDate").val(jsonData.StartDate);
    $("#EndDate").val(jsonData.EndDate);
    $("#hiddenbookid").val(bookId);
    document.getElementById("PrivateInfo").checked = Boolean(jsonData.PrivateInfo);
}

// Default page settings for Book.html
function defaultBookSettings(){
    const addBtn = document.getElementById("btnAddUpdate");
    if (addBtn != null){
        addBtn.innerText = "Add Book";
    }
    const cancelBtn = document.getElementById("btnCancel");
    if (cancelBtn != null){
        cancelBtn.hidden = true;
    }
}

function setimojiaction(inputType){
    if (inputType == "happy"){
        txt = "Good to know that you are happy, Keep going..!";
    }
    else if (inputType == "sad"){
        txt = "No worries...Things will get better."
    }

    $.ajax({
        url: '/savefeeling',
        type: 'POST',
        data: {"Feeling" : inputType},
        success: function(result){
            const msg = document.createElement('div');
            msg.className = "alert-success text-center";
            msg.id = "feelingtext";
            msg.appendChild(document.createTextNode(txt));
            document.getElementById('feelingmsgspace').appendChild(msg);
            setTimeout(removeMsg, 2000)
        }
    })
    function removeMsg(){
        document.getElementById("feelingtext").remove();
    }
}

function removeLearningMsg(){
    document.getElementById("learningresultalert").remove();
}

function showMonthlyExpenseDetails(){
    document.getElementById("currmnthexpensetxt").hidden = true;
    $.ajax({
        url: '/getcurrentmonthexpensedetails',
        type: 'GET',
        success: function (result){
            tbl = document.getElementById("curmonexpensetable");
            tblBody = document.getElementById("tbodyexpensedetail");
            if (tbl != null){
                htmlString = "";
                tbl.hidden = false;
                resultArray = result.split("`^`");
                jsonRecord = {}
                resultArray.forEach(function(record){
                    if (record.length != 0 ){
                        jsonRecord = JSON.parse(record)
                        htmlString = htmlString +
                                 '<tr><td>' + jsonRecord["Amount"]  + '</td>' +
                                 '<td>' + jsonRecord["ExpenseDate"] + '</td>' +
                                 '<td>' + jsonRecord["Category"]    + '</td>' +
                                 '<td>' + jsonRecord["Description"] + '</td></tr>';
                    }
                });
                tblBody.innerHTML= htmlString;
            }
        }
    })
}

//Function for showing the graphical representation for all expenses year wise.
//For the successful execution, return value will be the image file name.
//In case of error, return value will be 'error' string.

function showAllExpenseTrend(){
    document.getElementById('AllExpenseTrendTitle').hidden=true;
    $.ajax({
    url: '/getAllExpenseTrend',
    type:'GET',
    success: function(result){
        if (result != "error"){
            console.log(result);
            img_src=document.getElementById('AllExpenseTrend_img');
            img_src.src=result;
        }
        else{
            alert("Unable to access expense trend");
        }
    }})
}

// function for removing messages from the Journal form
function clearJournalMessage(){
    document.querySelector(".alert-success").remove();
}

// Access journal information while clicking the journal card
function journalCardClicked(journal_id){

    if (journal_id != null) {
        $.ajax({
            url : '/getjournalone',
            data : {"ObjectId" : journal_id},
            type : 'POST',
            success : function (result){
                if (result == "error"){
                    alert("Error occured while accessing the journal record!");
                }
                else{
                    jsondata = JSON.parse(result);
                    displayJournalRecord(jsondata.ObjectId,
                                         jsondata.Subject,
                                         jsondata.Notes,
                                         "Update");
                }

            }
        })
    }
}

// display Journal record in the input for view/update purpose
function displayJournalRecord(objectId,
                              subject,
                              notes,
                              btn_text){
    $('#subject_input').val(subject);
    $('#subject-text').val(notes);

    /* Set the hidden field for object id*/
    document.getElementById("objectid_input").value = objectId;

    //Change the save button label
    document.getElementById("btn_journal_Save").innerText = btn_text;

    //set the focus to subject element
    document.getElementById("subject_input").focus();

}

function journal_cancel_clicked(e){
    displayJournalRecord("","","","Save");
}

function getAllReminders(){
    $.ajax({
    url : '/getallreminders',
    type : 'GET',
    success : function (result){
        if (result==""){
            alert('No reminders');
        }
        else{
            reminder_all = document.getElementById('reminder_all');
            resultArray = result.split("`^`");
            jsonRecord={};
            htmlString="<table class='table table-striped'><tbody><thead>" +
            "<tr><th>Id</th>" +
            "<th>Name</th>" +
            "<th>StartDate</th>" +
            "<th>ReminderDate</th>" +
            "<th>IntervalPeriod</th>" +
            "<th>Comments</th>" +
            "<th></th>" +
            "</tr></thead><tbody>";
            quotes="'";
            resultArray.forEach(function(record){
                if (record.length!= 0){
                    jsonRecord=JSON.parse(record);
                    htmlString=htmlString+
                    '<tr>'+
                    '<td>' + jsonRecord['ReminderId']      + '</td>'+
                    '<td>' + jsonRecord['EventName']     + '</td>'+
                    '<td>' + jsonRecord['StartDate']      + '</td>'+
                    '<td>' + jsonRecord['ReminderDate']   + '</td>'+
                    '<td>' + jsonRecord['IntervalPeriod'] + '</td>'+
                    '<td>' + jsonRecord['Comments']       + '</td>'+
                    '<td>' +  "<button class=\"btn btn_icon\" onclick=\"reminder_row_delete(\'"+jsonRecord['_id']+"\')\"><i class=\"fa fa-trash\"></i></button>" + '</td>'
                    + '</tr>';
                    }
            });
            htmlString = htmlString + '</tbody></table>';
            reminder_all.innerHTML = htmlString;
            }
        }
    })
}

function reminder_row_delete(id){
    if (confirm('Delete Reminder?')==true){
        $.ajax({
            url : '/delete_reminder_one',
            data : {"_id" : id},
            type : 'POST',
            success : function (result){
                if (result == "error"){
                    alert("Error occured while deleting the journal record!");
                }
                else{
                    getAllReminders();
                }
            }
        })
    }
}