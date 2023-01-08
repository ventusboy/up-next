import { Home } from './components/Home';
import './main.scss';
import './input.scss';


function App() {
  return (
    <div className="App">
      <div
        className='welcome-txt'
      >
        Welcome, please enter your code to connect your device
      </div>
      <Home></Home>
    </div>
  );
}

export default App;
