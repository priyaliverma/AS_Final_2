// Register Sign-Up Modal Component
Vue.component('modal', {
    template: '#modal-template'
});

new Vue({
    el:'#desc',
    delimiters: ['${', '}'],
    data: {
        showModal1: false,
        header1: 'STEP 1: USER INFORMATION',
        name: 'Name',
        birth_date: 'Date of Birth (MM/DD/YYYY)',
        email: 'Email',
        password: 'Password',
        confirm_password: 'Confirm Password',
        showModal2: false,
        header2: 'STEP 2: PHYSICAL STATS',
        height: 'Height (Feet + inches/Meters + cm)',
        weight: 'Weight (lbs or kilos)',
        showModal3: false,
        header3: 'STEP 3: EXPERIENCE',
        training_exp: 'Training Experience (Years and Months)',
        primary_sports: 'Primary Sports (Please list a maximum of three)',
        rpe_exp: 'Experience Using RPE?',
        known_maxes: 'Known Max Lifts (Leave Blank if Unknown)',
        squat: 'Squat',
        bench: 'Bench',
        deadlift: 'Deadlift',
        overhead_press: 'Overhead Press', 
        power_clean: 'Power Clean', 
        clean_and_jerk: 'Clean and Jerk',
        snatch: 'Snatch',
        other: 'Other',
        showModal4: false,
        header4: 'You\'re all done! Thanks for signing up!',
        showModal5: false,
        header5: 'LOG IN',
        email2: 'Email', 
        password2: 'Password'
    }
});

