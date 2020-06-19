import axios from 'axios'

export const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000/',
  timeout: 10000,
});


export const register = newUser => {
  return axiosInstance
    .post('api/register', {
      first_name: newUser.first_name,
      last_name: newUser.last_name,
      username: newUser.username,
      password: newUser.password
    })
    .then(response => {
      console.log('Registered')
    })
}

export const photos = newUser => {
  return axiosInstance
    .get('api/allphotos')
    .then(response => {
      console.log(response);
      return response;
    })
}

export const login = user => {
  return axiosInstance
    .post('api/login', {
      username: user.username,
      password: user.password
    })
    .then(response => {
      console.log(response.data);

      localStorage.setItem('password', response.data.password)
      localStorage.setItem('username', response.data.username)
      localStorage.setItem('first_name', response.data.first_name)
      localStorage.setItem('last_name', response.data.last_name)
      
      return response.data
    })
    .catch(err => {
      console.log(err)
    })
}

export const getProfile = user => {
  return axiosInstance
    .get('users/profile', {
      //headers: { Authorization: ` ${this.getToken()}` }
    })
    .then(response => {
      console.log(response)
      return response.data
    })
    .catch(err => {
      console.log(err)
    })
}