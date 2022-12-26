// @flow 

import {  useRef, useState } from "react";
import { useEffect, useCallback } from 'react';
import axios from "axios";
import { getPlaybackState, getUserQueue } from '../functions/functions'


export const Home = (props) => {

    const [piCode, setPiCode]  = useState('');
    const [initialData, setInitialData] = useState('');
    let isMounted = useRef(false)
    let baseUrl = process.env.REACT_APP_API_URL

    //const logout = useCallback(
    /*function logout() {
        localStorage.removeItem('authDataTemp')
    }*/
    //, [])

    const getAuthData = useCallback(async ({ code, refresh_token, state }) => {
        //expiration.current = null
        console.log(code)
        //console.log(new URLSearchParams(window.location.search))
        if (!code ){//|| !state)) {
            //logout()
            return null
        }
        let authData = JSON.parse(localStorage.getItem('authDataTemp'))


        if(!authData || authData.exp < Date.now() ){//|| !authData.state){
            //let { state } = new URLSearchParams(window.location.search).get('state')
            //console.log(state)
            
            let piCode = localStorage.getItem('piCode') || ''
            let { data } = await axios.get(baseUrl + '/getToken', { params: { code, refresh_token, piCode } })

            if (data.access_token) {
                data.exp = Date.now() + (data.expires_in - 300) * 1000 // "expires" 5 mins early
                //data.state = state
                data.piCode = piCode
                let tempHeader = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + data.access_token,
                    "Accept": 'application/json'
                }
                data.headers = tempHeader
                localStorage.setItem('authDataTemp', JSON.stringify(data))
            }
            authData = data
        }
        console.log(authData)
        return authData.headers

    }, [baseUrl])

    useEffect(() => {

        async function init({ code }){
            //let { state } = new URLSearchParams(window.location.search).get('state')
            let headers = await getAuthData({ code })
            //console.log(localStorage.getItem('authDataTemp'))
            //console.log(headers)
            if(headers){
                let data = await getPlaybackState({headers})
                console.log(data)
                let queue = await getUserQueue({headers})
                console.log(queue)
            }
        }
        if(isMounted.current){
            return
        }

        let urlObj = new URLSearchParams(window.location.search)
        let tempAuth = {
            //state: urlObj.get('state'),
            code: urlObj.get('code')
        }
        console.log(tempAuth)
        if(tempAuth.code){
            setInitialData(tempAuth)
        }

        if(initialData.code && isMounted.current === false){
            init(initialData);
            isMounted.current = true
        }

    }, [ initialData,isMounted, getAuthData])



    return (
        <div style={{
            zIndex: 0,
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
        }}>

            <div className="centered">
                <div className="group">
                    <input
                        type='text'
                        value={piCode}
                        id="code"
                        required
                        //placeholder='input code here'
                        onChange={(event) => {
                            setPiCode(event.target.value)
                        }}
                    />
                    <label htmlFor="code">
                        Display Code
                    </label>
                    <div className="bar"></div>
                </div>

            </div>


            <button
                className="button-68"
                /*onClick={() => {
                    console.log(initialData)
                }}*/
            >
                <a 
                style={{ textDecoration: 'none', color: 'black' }} 
                href={piCode ? baseUrl + `/login?userCode=${piCode}` : ''}
                onClick={(() => {
                    localStorage.setItem('piCode', piCode)
                })}                
                >
                    Submit
                </a>
            </button>
        </div>
    );
};