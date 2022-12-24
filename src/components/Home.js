// @flow 

import { useState } from "react";
import { useEffect, useCallback } from 'react';
import axios from "axios";


export const Home = (props) => {

    const [piCode, setPiCode]  = useState('');
    const [code] = useState(new URLSearchParams(window.location.search).get('code'));
    let baseUrl = process.env.REACT_APP_API_URL

    //const logout = useCallback(
    function logout() {
        localStorage.removeItem('authDataTemp')
    }
    //, [])

    const getAuthData = useCallback(async ({ code, refresh_token }) => {
        //expiration.current = null

        if (!code && !refresh_token) {
            logout()
            return
        }

        let { data } = await axios.get(baseUrl + '/getToken', { params: { code, refresh_token } })

        if (data.access_token) {
            data.exp = Date.now() + (data.expires_in - 300) * 1000 // "expires" 5 mins early

            let tempHeader = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + data.access_token,
                "Accept": 'application/json'
            }
            data.headers = tempHeader
            localStorage.setItem('authDataTemp', JSON.stringify(data))
        }

        return data
    }, [baseUrl])

    useEffect(() => {
        getAuthData({ code })
        console.log(localStorage.getItem('authDataTemp'))
    }, [code, getAuthData])


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
                onClick={() => {
                    console.log(code)
                }}
            >
                <a style={{ textDecoration: 'none', color: 'black' }} href={baseUrl + '/login'}>
                    Submit
                </a>
            </button>
        </div>
    );
};