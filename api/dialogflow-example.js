'use strict';

// Dot Env
require('dotenv').config()

const dialogflow = require('dialogflow')
const fs = require('fs')
const _ = require('lodash')
const Promise = require('bluebird')
const serverless = require('serverless-http')
const bodyParser = require('body-parser')
const express = require('express')
const cors = require('cors')({origin: true})
const superagent = require('superagent')
const app = express()
const admin = require('firebase-admin')

// Initialize Firebase Admin
var serviceAccount = require('./secret/firebase-adminsdk.json')
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
})
var db = admin.firestore()

// const intentId = '04d51713-6760-4b20-99ae-5e69bebab904'
// const intentId = '04d51713-6760-4b20-99ae-5e69bebab904'
const intentId = 'acec4907-e038-4bd3-bf10-7b223c05e0a9'

// Initialize Dialog Flow
const dfProjectId = process.env.GCLOUD_PROJECT_ID || ''
const languageCode = 'en'
const dialogFlowSessionClient = new dialogflow.SessionsClient({
  keyFilename:'./secret/dialogflow.json'
})

const intentsClient = new dialogflow.IntentsClient({
  keyFilename:'./secret/dialogflow-editor.json'
});

const blackList = [
  
]


const createTrainingPhrase = (text) => {
  return {
    parts: [
      {
        text,
        // entityType: "",
        // alias: "",
        // userDefined: false
      }
    ],
    type: "EXAMPLE",
  }
}

//TODO validate phrases


const formattedName = intentsClient.intentPath(dfProjectId, intentId);
const newRawPhrases = ['new text', 'lol lol']
intentsClient.getIntent({name: formattedName, intentView: 1 })
  .then(responses => {
    const originalIntent = responses[0];
    console.log(JSON.stringify(originalIntent, null ,2))
    return originalIntent
  })
  .then(originalIntent => {
    const intent = {
      ...originalIntent,
      trainingPhrases: originalIntent.trainingPhrases
                        .concat(newRawPhrases.map(createTrainingPhrase))
    };
    console.log('[UPDAE INTENT]')
    console.log(JSON.stringify(intent, null ,2))
    intentsClient.updateIntent({ intent, languageCode })
      .then(responses => {
        const response = responses[0];
        console.log('Updated')
        console.log(response)
        // res.send(response)
      })
      .catch(err => {
        console.error(err);
      });
  })
  .catch(err => {
    console.error(err);
    res.status(400).send(err)
  });


