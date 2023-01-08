import axios from "axios";
const spotifyUrl = 'https://api.spotify.com/v1'

export async function getPlaybackState({ headers }){
    try {
        let { data } = await axios.get(spotifyUrl + '/me/player', { headers })
        //console.log(data)
        return data
    } catch (error) {
        console.log(error)
        return null
    }
}

export async function getUserQueue({ headers }){
    try {
        let { data } = await axios.get(spotifyUrl + '/me/player/queue', { headers })
        //console.log(data)
        return data
    } catch (error) {
        console.log(error)
        return null
    }
}
