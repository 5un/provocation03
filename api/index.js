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

const intentId = '04d51713-6760-4b20-99ae-5e69bebab904'
// const intentId = 'acec4907-e038-4bd3-bf10-7b223c05e0a9'

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

app.use(bodyParser.json({ strict: false }))

app.get('/', function (req, res) {
  res.send('Hello World!')
})

app.get('/phrases', function (req, res) {  
  cors(req, res, () => {

    const formattedName = intentsClient.intentPath(dfProjectId, intentId);
    intentsClient.getIntent({
      name: formattedName, 
      intentView: 1,
    })
      .then(responses => {
        const response = responses[0];
        const phrases = (response.trainingPhrases || [])
                          .map(tp => {
                            return tp.parts.map(p => (p.text || '')).join(' ')
                          })
        //TODO: limits and pagination
        res.send(phrases.reverse())
      })
      .catch(err => {
        console.error(err);
        res.status(400).send(err)
      });
    
  })
})

const createTrainingPhrase = (text) => {
  return {
    parts: [{ text }],
    type: "EXAMPLE",
  }
}

app.post('/phrases', function (req, res) {  
  cors(req, res, () => {
    //TODO validate phrases
    if(!req.body.phrases) {
      res.status(400).send({ message: 'phrases parameter is required' })
      return
    }

    const formattedName = intentsClient.intentPath(dfProjectId, intentId);
    const newRawPhrases = req.body.phrases || []
    intentsClient.getIntent({name: formattedName, intentView: 1 })
      .then(responses => {
        const originalIntent = responses[0];
        return originalIntent
      })
      .then(originalIntent => {
        const intent = {
          ...originalIntent,
          trainingPhrases: originalIntent.trainingPhrases
                            .concat(newRawPhrases.map(createTrainingPhrase))
        };
        intentsClient.updateIntent({ intent, languageCode })
          .then(responses => {
            const response = responses[0];
            res.send({ success: true })
          })
      })
      .catch(err => {
        console.error(err);
        res.status(400).send(err)
      });
  })
})

module.exports.handler = serverless(app);
