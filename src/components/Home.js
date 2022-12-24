// @flow 

import { useState } from "react";

export const Home = (props) => {
    const [code, setCode] = useState('')

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
                        value={code}
                        id="code"
                        required
                        //placeholder='input code here'
                        onChange={(event) => {
                            setCode(event.target.value)
                        }}
                    />
                    <label for="code">
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
                Submit
            </button>
        </div>
    );
};