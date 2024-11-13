/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./app/templates/**/*.{html, js}"],
    theme: {
        extend: {
            fontFamily: {
                montserrat: ['Montserrat', 'sans-serif'],
                roboto: ['Roboto', 'sans-serif'],
            },
            keyframes: {
                flash: {
                    '0%': {opacity: '0'},
                    '50%': {opacity: '1'},
                    '100%': {
                        opacity: '0',
                        display: 'none',
                    }
                },
            },
                animation: {
                    'flash': 'flash 5s ease-in-out forwards'
                },
                colors: {
                    darkerCharcoal: '#1E1E1E',
                    charcoal: '#2D2F33',
                    steel: '#4A4D52',
                    electricBlue: '#3A86FF',
                    goldenYellow: '#FFD166',
                    slateWhite: '#E0E1DD',
                    lightSteel: '#9CA3AF',
                },
            },
        },
        plugins: [],
    }

