const functions = require('firebase-functions');
const express = require('express');
const cors = require('cors');

const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();

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

app.get('/getCode/:piCode', async (req, res) => {
    let { piCode } = req.params
    if (piCode.length < 5) {
        res.send(new Error('Invalid piCode'))
    }

    let tokenDataRef = db.collection('code-piCode-pair').doc(piCode)
    let tokenData = await tokenDataRef.get()
    if (tokenData.exists) {
        data = tokenData.data()
        if(data.exp > Date.now() / 1000)
            res.send(data)
        else {
            tokenDataRef.delete()
            res.status(401).send({
                error: 'access token has expired'
            })
        }
    } else {
        res.status(404).send({
            error: 'piCode DNE'
        })
    }

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
    //let { userCode } = req.query

    var state = generateRandomString(16);
    var scope = 'user-read-private user-read-email streaming user-read-playback-state';

    let url = 'https://accounts.spotify.com/authorize?' +
        new URLSearchParams({
            response_type: 'code',
            client_id: client_id,
            scope: scope,
            redirect_uri: redirect_uri,
            state
        })
    //db.collection('code-state-pair').doc(state).set({ userCode })
    //db.collection('userCodes').doc(userCode).set({ userCode })

    //console.log(url)
    //db. set state with code

    res.redirect(url);
});

app.get('/getToken', async (req, res) => {
    const { URLSearchParams } = require('url');
    const axios = require('axios');
    //console.log(req.query)
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
        let { piCode } = req.query
        db.collection('code-piCode-pair').doc(piCode).set({
            ...data,
            piCode,
            exp: Math.floor(Date.now() / 1000) + 3600
        }, { merge: true })
        res.send(data)
    } catch (error) {
        console.error(error)
        res.send(error)
    }
})

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

exports.app = functions.https.onRequest(app);
