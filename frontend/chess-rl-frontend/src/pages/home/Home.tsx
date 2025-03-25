import React from "react"
import "./Home.css"
import Footer from "../../components/Footer";

const Home: React.FC = () => {
    return (
        <div className="container-fluid home-bg w-100">
            <div className="row h-75">
                <div className="col">
                    <div className="col d-flex flex-column bg-light rounded-3 shadow bg-opacity-75 w-25 h-100 ml-30p mt-5p">
                        <div className="pt-15p text-center">
                            <h1>ChessRl</h1>
                            <img className="mx-auto d-block" src="/assets/chess-rl-logos/chess-rl-logo128.png" alt="ChessRl" />
                        </div>
                        <div className="col d-flex flex-column align-items-center pt-20p gap-3">
                            <button className="btn btn-dark w-50 py-2">See How AI Agents Play</button>
                            <button className="btn btn-dark w-50 py-2">Play a Game Against AI Agent</button>
                            <a className="w-50" href="https://github.com/f1scher7/chess-rl" target="_blank" rel="noreferrer">
                                <button className="btn btn-dark w-100 py-2">About</button>
                            </a>
                        </div>
                        <div className="mt-auto">
                            <Footer />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};


export default Home;
