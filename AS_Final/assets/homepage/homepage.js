// Register Sign-Up Modal Component
Vue.component('modal', {
    template: '#modal-template'
})

var Vue_1 = new Vue({
    el:'#sign-up',
    delimiters:['${', '}'], 
    data: {
        showModal: false,
        showModal_Two: false,
        header: 'SIGN UP',
        name: 'Name',
        email: 'Email',
        password: 'Enter Password Here',
        confirm_password: 'Please Retype Password'
    }
})



var Vue_2 = new Vue({
    el:'#log-in',
    delimiters:['${', '}'], 
    data: {
        showModal: false,
        header: 'LOG IN',
        email: 'Email',
        password: 'Password',
    }
})