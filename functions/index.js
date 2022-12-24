const functions = require('firebase-functions');
const express = require('express');
const cors = require('cors');
let db = null;
const app = express()

app.use(cors())

const client_id = process.env.CLIENT_ID;
const client_secret = process.env.CLIENT_SECRET
const redirect_uri = process.env.REDIRECT;

function checkDB() {
  if (db === null) {
    const admin = require('firebase-admin');
    admin.initializeApp();
    db = admin.firestore();

  }
  return db
}

app.get('/', async (req, res) => {
  res.send("hello world")
})


app.get('/login', (req, res) => {
  const { URLSearchParams } = require('url');
  var generateRandomString = function (length) {
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for (var i = 0; i < length; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  };

  var state = generateRandomString(16);
  var scope = 'user-read-private user-read-email user-library-read playlist-read-private playlist-modify-private';

  let url = 'https://accounts.spotify.com/authorize?' +
    new URLSearchParams({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state
    })
  console.log(url)

  res.redirect(url);
});

app.get('/getToken', async (req, res) => {
  const { URLSearchParams } = require('url');
  const axios = require('axios');
  console.log(req.query)
  let code = req.query.code || null;
  let refresh_token = req.query.refresh_token || null
  let url = 'https://accounts.spotify.com/api/token'

  let headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + Buffer.from(client_id + ':' + client_secret).toString("base64")
  }

  const formData = new URLSearchParams()

  if (refresh_token) {
    formData.append("refresh_token", refresh_token)
    formData.append("grant_type", "refresh_token")
  } else {
    formData.append("code", code)
    formData.append("redirect_uri", redirect_uri)
    formData.append("grant_type", "authorization_code")
  }


  try {
    let { data } = await axios.post(url, formData, { headers: headers })
    //console.log(data)
    res.send(data)
  } catch (error) {
    console.error(error)
    //console.log(error.response?.data)
    //console.log('error')
    res.send(error)
  }
})

function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

exports.app = functions.https.onRequest(app);
