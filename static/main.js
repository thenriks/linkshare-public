const BACK = 'http://127.0.0.1:8000'

Vue.use(VueRouter);

var store = {
  debug: true,
  state: {
    links: [],
    username: "",
    user_id: 0,
    token: "",
    userInfo: ""
  },
  setLinks (newValue) {
    this.state.links = newValue
  }
}

// TODO: return url argument 
const Login = {
  data: function () {
    return {
      sharedState: store.state,
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
            this.sharedState.userInfo = response.data.info;
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
              <div><b>Your info:</b> {{sharedState.userInfo}}</div>\
              <div>\
                Add link:<br>\
                Url: <input v-model="newUrl" maxlength="2000"><br>\
                Info: <input v-model="newInfo" maxlength="100"><br>\
                <button v-on:click="sendNewLink">Add</button><br>\
              </div>\
              My links:<br>\
              <table id=\"user-links\"> \
                <tr v-for=\"link in sharedState.links\" :key=\"link.url\"> \
                  <td><a v-bind:href=link.url target=\"_blank\">Go</a></td>\
                  <td>{{ link.info }}</td> \
                  <td><td><button v-on:click="switchState(link.id)" v-if="link.hidden">Show</button>\
                  <button v-on:click="switchState(link.id)" v-else>Hide</button></td>\
                </tr> \
              </table></div>',
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
    },
    switchState: function(id) {
      data = {
        linkId: id 
      }

      axios.post('/switch_state', data, { headers: { Authorization: this.sharedState.token }})
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
      userInfo: "",
      sharedState: store.state,
    }
  },
  created: function() {
    this.getLinks();
    this.getUserInfo();
  },
  watch: {
    '$route': 'getLinks'
  },
  template: '<div>Links for user {{ $route.params.id }} <br> \
              <b>Info: </b> {{this.userInfo}} <br>\
              <div v-if="loading"> \
                Loading... \
              </div> \
              <div v-else> \
                <table id=\"user-links\"> \
                  <tr v-for=\"link in userLinks\" :key=\"link.url\" v-if="!link.hidden"> \
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
    },
    getUserInfo() {
      this.loading = true;
      axios.get('/user_info/' + this.$route.params.id)
              .then(response => {
                this.loading = false;
                this.userInfo = response.data;
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
  template: '<div>Create new account.<br>\
                Username: <input v-model="newUname" maxlength="32"><br>\
                E-mail: <input v-model="newEmail" maxlength="64"><br>\
                Password: <input v-model="newPass" maxlength="64"><br>\
                User info: <textarea v-model="newUserInfo" maxlength="300"></textarea><br>\
                <button v-on:click="sendSignUp">Send</button><br>\
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

const FrontPage = {
  data: function () {
    return {
      loading: false,
      sharedState: store.state,
      newUsers: []
    }
  },
  created: function() {
    this.getUsers();
  },
  template: '<div>\
              <div>Link sharing website. Under development, not meant for real use, database may be wiped anytime.</div>\
              <div>Source: https://github.com/thenriks/linkshare-public</div>\
              <div>Newest members:</div>\
              <div v-if="loading"> \
                Loading... \
              </div> \
              <div v-else>\
                <table id=\"new-users\"> \
                  <tr v-for=\"user in newUsers\" :key=\"user.username\"> \
                    <td><a v-bind:href=user.id> {{user.username}} </a></td>\
                  </tr> \
                </table> \
              </div>\
            </div>',
  methods: {
    getUsers() {
      this.loading = true;
      axios.get('/new_users/')
              .then(response => {
                this.loading = false;
                this.newUsers = response.data;
              })
              .catch(e => {
                console.log(e);
              });
    }
  }
};

const routes = [
  { path: '/', component: FrontPage},
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
