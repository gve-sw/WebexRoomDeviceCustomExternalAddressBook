 /**
 * @license
 * Copyright (c) 2021 Cisco and/or its affiliates.
 *
 * This software is licensed to you under the terms of the Cisco Sample
 * Code License, Version 1.1 (the "License"). You may obtain a copy of the
 * License at
 *
 *                https://developer.cisco.com/docs/licenses
 *
 * All use of the material herein must be in accordance with the terms of
 * the License. All rights not expressly granted by the License are
 * reserved. Unless required by applicable law or agreed to separately in
 * writing, software distributed under the License is distributed on an "AS
 * IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied.
 */
const xapi = require('xapi');

const BTN_EXT_PHONEBOOK_WIDGET = 'ext_phonebook'

const KEYBOARD_TYPES = {
    NUMERIC     :   'Numeric'
  , SINGLELINE  :   'SingleLine'
  , PASSWORD    :   'Password'
  , PIN         :   'PIN'
}
const CALL_TYPES = {
    AUDIO     :   'Audio'
  , VIDEO     :   'Video'
}

const phBkServerHost='10.0.0.1';
const phBkServerPort='5001';
const theURLBase='http://'+phBkServerHost+":"+phBkServerPort;

var resultBody=[];

// theOptionsStrings contains the names from the phonebook entries
// to display to give users a choice
var theOptionsStrings=[];

// theOptionsIndex contains the actual index within the results that came back
// from the phonebook (REST call to server) so we can extract the numbers to dial
var theOptionsIndex=[];

// theOptionsDest will contain the actual numbers to dial once
// a directory entry is selected
var theOptionsDest=[];

const SEARCHFORM_ID = 'searchform';
const SELECTIONFORMNAMES_ID = 'selectionformnames';
const SELECTIONFORMNUMBERS_ID = 'selectionformnumbers';

xapi.config.set('HttpClient AllowHTTP',"True");
xapi.config.set('HttpClient AllowInsecureHTTPS',"True");

xapi.command("HttpClient Allow Hostname Clear");
xapi.command("HttpClient Allow Hostname Add", {Expression: phBkServerHost});


// to add delays when or if needed. Could be helpful if you want uesrs to see the Zoom or BJN main welcome screen a couple of seconds before
// putting up the form to enter conference ID
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function showSearchInput(text, template){

    xapi.command("UserInterface Message TextInput Display", {
          InputType: KEYBOARD_TYPES.SINGLELINE
        , Placeholder: template
        , Title: "External PhoneBook Search"
        , Text: text
        , SubmitText: "Submit"
        , FeedbackId: SEARCHFORM_ID
    }).catch((error) => { console.error(error); });
}

// catch event triggered when user filled out search form
xapi.event.on('UserInterface Message TextInput Response', (event) => {
    switch(event.FeedbackId){
        case SEARCHFORM_ID:
        // this is after they entered something in the search form
            console.log('searching in address book');
            var theString=event.Text;
            var theJSON=JSON.stringify({search_string:theString});
            console.log('Using search term: ',theString);
            console.log('JSON version: ',theJSON)
            xapi.command('HttpClient Post',
                                { AllowInsecureHTTPS: "True",
                                  Header:["Content-Type: application/json; charset=UTF-8"],
                                  ResultBody: 'PlainText',
                                  Url: theURLBase+"/searchall"
                                },
                                theJSON
                        ).then((resultado)=>{
                          resultBody = JSON.parse(resultado.Body);
                          console.log("HTTP Get returned: ",resultBody);

                          // now construct the options to search for
                          //TODO: if there are more than 5 results, then put "More...." on the last option and
                          //      create a special case for that option to just put up this same form again with the
                          //      next 4 (if still more) or 5 entries from the list. Use theOptionsIndex[4]=-2 as the indicator
                          //      For this to work, i has to be a global variable so we can keep incrementing it as we select
                          //      more entries from the resultBody list, which already is a global.
                          var i=0;
                          while (i<5 && i<resultBody.length)
                          {
                            theOptionsStrings[i]=resultBody[i].last+", "+resultBody[i].first;
                            theOptionsIndex[i]=i;
                            i=i+1;
                          }
                          // make sure the array has at least 5 elements
                          while (i<5)
                          {
                            theOptionsStrings[i]="";
                            theOptionsIndex[i]=-1;
                            i=i+1;
                          }

                          if (theOptionsStrings[0]!=="")  {
                          // upon return, put up another form that asks them to select and dial
                            sleep(200).then(() => {
                              xapi.command('UserInterface Message Prompt Display',
                                { Title: 'Search results', Text:'Select a user to display numbers to call:',
                                  FeedbackId: SELECTIONFORMNAMES_ID,
                                  Duration:30,
                                  'Option.1':theOptionsStrings[0],
                                  'Option.2':theOptionsStrings[1],
                                  'Option.3':theOptionsStrings[2],
                                  'Option.4':theOptionsStrings[3],
                                  'Option.5':theOptionsStrings[4]});
                                });
                            console.log('Done prompting selection from names that returned...');
                          }
                          else
                          {
                            xapi.command("UserInterface Message Alert Display", {
                                          Title: "Not found"
                                          , Text: "Your query returned 0 results"
                                          , Duration: 5
                                      });
                          }
                        });


            break;

    }
});

// catch events upon selection in multiple option forms
// for selecting entries to dial and numbers within those entries
xapi.event.on('UserInterface Extensions Panel Clicked', (event) => {
    //check to see if external phonebook has been requested
    if(event.PanelId == BTN_EXT_PHONEBOOK_WIDGET){
            showSearchInput("Please enter a last name, first name or user ID:", "");
    }

});

xapi.event.on('UserInterface Message Prompt Response', (event) => {
    switch(event.FeedbackId){
      case SELECTIONFORMNAMES_ID:
        // This is once they selected from a list of names that came back in the search
            console.log('selecting name');
            //selectedName=event.Text;
            var nameOptionId=event.OptionId;
            let theIndex=nameOptionId-1;
            // TODO: If the ID is for Option 5 and looking in the theOptionsIndex[theIndex] we see a special "more"
            //       indicator (i.e. -2) then display the SearchResults form with the next 4 or 5 entries.
            console.log('Selected name option: ',nameOptionId);
            //now I have to match the option selected with what I set when I filled out the form!
            // with that, I can extract the numbers to add to the options below
            if (theOptionsIndex[theIndex]!==-1)
            {
              theOptionsDest[0]=resultBody[theOptionsIndex[theIndex]].officephone;
              theOptionsDest[1]=resultBody[theOptionsIndex[theIndex]].mobilephone;
              theOptionsDest[2]=resultBody[theOptionsIndex[theIndex]].email;
              let dialogTitle;
              dialogTitle=resultBody[theOptionsIndex[theIndex]].last+", "+resultBody[theOptionsIndex[theIndex]].first;

              sleep(200).then(() => {
                            xapi.command('UserInterface Message Prompt Display',
                                { Title: dialogTitle, Text:'Select a phone number or URI to call:',
                                  FeedbackId: SELECTIONFORMNUMBERS_ID,
                                  Duration:30,
                                  'Option.1':"O: "+theOptionsDest[0],
                                  'Option.2':"M: "+theOptionsDest[1],
                                  'Option.3':"E: "+theOptionsDest[2]});
                                });
                    console.log('Done prompting numbers from name...');
            }
            else
            {
                xapi.command("UserInterface Message Alert Display", {
                                          Title: "Invalid"
                                          , Text: "Invalid selection"
                                          , Duration: 5
                                      });
            }
            break;

        case SELECTIONFORMNUMBERS_ID:
        // This is once they selected from a list of numbers of a specific name to dial
            console.log('dialing number selected');
            var numberOptionId=event.OptionId;
            let theDestIndex=numberOptionId-1;
            console.log('Selected number option: ',numberOptionId);
            xapi.command("dial", {Number: theOptionsDest[theDestIndex]});
            break;
    }
});

