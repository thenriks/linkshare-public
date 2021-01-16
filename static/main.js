const BACK = 'http://127.0.0.1:8000'

Vue.use(VueRouter);

var store = {
  debug: true,
  state: {
    links: [],
    username: "",
    user_id: 0,
    token: ""
  },
  setLinks (newValue) {
    this.state.links = newValue
  }
}

// TODO: return url argument 
const Login = {
  data: function () {
    return {
      email: "",
      pass: "",
      token: ""
    }
  },
  template: '<div>Username: <input v-model="email"><br>Password: <input v-model="pass"><br><button v-on:click="sendLogin">Login</button><br></div>',
  methods: {
    sendLogin: function() {
      console.log("sendLogin");
      var formData = new FormData();
      formData.append('username', this.email);
      formData.append('password', this.pass);
      console.log(this.email);
      axios.post('/auth/token', formData)
          .then(response => {
            this.res = response;
            this.token = response.data.token_type + ' ' + response.data.access_token;
            this.$root.$emit('setToken', this.token, this.email, response.data.user_id);
            console.log(this.token);
          })
          .catch(e => {
            console.log(e);
          });
    }
  }
};

const User = { 
	data: function () {
		return {
      sharedState: store.state,
      newUrl: '',
      newInfo: ''
		}
	},
	template: '<div>Share your links: https://thawing-savannah-46774.herokuapp.com/#/v/{{sharedState.user_id}}<br> \
              <div>\
                Add link:<br>\
                Url: <input v-model="newUrl"><br>\
                Info: <input v-model="newInfo"><br>\
                <button v-on:click="sendNewLink">Add</button><br>\
              </div>\
              My links:<br>\
              <table id=\"user-links\"> \
                <tr v-for=\"link in sharedState.links\" :key=\"link.url\"> \
                  <td><a v-bind:href=link.url target=\"_blank\">Go</a></td>\
                  <td>{{ link.info }}</td> \
                </tr> \
              </table>',
  methods: {
    sendNewLink: function() {
      console.log("sendNewLink");
      data = {
        url: this.newUrl,
        info: this.newInfo,
        uid: this.sharedState.user_id
      }
      if (!data.url.startsWith('http://') || !data.url.startsWith('https://')) {
        data.url = 'http://' + data.url;
      }
      axios.post('/add_link', data, { headers: { Authorization: this.sharedState.token }})
          .then(response => {
            // Update link list
            axios.get('/links/' + this.sharedState.user_id)
              .then(response => {
                this.sharedState.links = response.data;
              })
              .catch(e => {
                console.log(e);
              });
          })
          .catch(e => {
            console.log(e);
          });
    }
  }
}

const ShowUser = {
  data: function () {
    return {
      loading: false,
      userLinks: [],
      sharedState: store.state,
    }
  },
  created: function() {
    this.getLinks();
  },
  watch: {
    '$route': 'getLinks'
  },
  template: '<div>Links for user {{ $route.params.id }} <br> \
              <div v-if="loading"> \
                Loading... \
              </div> \
              <div v-else> \
                <table id=\"user-links\"> \
                  <tr v-for=\"link in userLinks\" :key=\"link.url\"> \
                    <td><a v-bind:href=link.url target=\"_blank\">Go</a></td>\
                    <td>{{ link.info }}</td> \
                  </tr> \
                </table> \
              </div> \
            </div>',
  methods: {
    getLinks() {
      this.loading = true;
      axios.get('/links/' + this.$route.params.id)
              .then(response => {
                this.loading = false;
                this.userLinks = response.data;
              })
              .catch(e => {
                console.log(e);
              });
    }
  }
};

const SignUp = {
  data: function () {
    return {
      sharedState: store.state,
      newUname: '',
      newEmail: '',
      newPass: '',
      newUserInfo: ''
    }
  },
  template: '<div>Create new account.\
              <div>\
                Username: <input v-model="newUname"><br>\
                E-mail: <input v-model="newEmail"><br>\
                Password: <input v-model="newPass"><br>\
                <button v-on:click="sendSignUp">Send</button><br>\
              </div> \
            </div>',
  methods: {
    sendSignUp: function() {
      data = {
        username: this.newUname,
        email: this.newEmail,
        password: this.newPass,
        info: this.newUserInfo 
      }
      axios.post('/add_user', data)
          .then(response => {
            this.$router.push("/");
          })
          .catch(e => {
            console.log(e);
          });
    }
  }
};

const routes = [
  { path: '/login', component: Login },
  { path: '/user/:id', component: User },
  { path: '/v/:id', component: ShowUser },
  { path: '/signup', component: SignUp }
]

const router = new VueRouter({
  routes
})

var app = new Vue({
	router,
  el: '#app',
  data: {
    status: "Logged off",
    logged: false,
    sharedState: store.state
  },
  created: function () {
    this.$root.$on('setToken', (token, email, id) => {
      this.sharedState.token = token;
      this.sharedState.username = email;
      if (token != "") {
        this.status = "Logged in as " + this.sharedState.username;
        this.sharedState.user_id = id;
        this.logged = true;
        axios.get('/links/' + this.sharedState.user_id)
          .then(response => {
            this.sharedState.links = response.data;
          })
          .catch(e => {
            console.log(e);
          });
        this.$router.push("/user/" + this.sharedState.username);
      }
      console.log(token);
    });
  },
  methods: {
    logOut: function () {
      console.log("logOut");
      this.sharedState.links = [];
      this.sharedState.token = "";
      this.logged = false;
      this.status = "Logged off";
      this.$router.push("/login");
    }
  }
}).$mount('#app')
