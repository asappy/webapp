function closepage(){

	window.close();

}
// function GetDevices() {
//     let _self = this
//     return new Promise(function(resolve, reject) {
   
//       _self.axios({
//         method: 'GET',
//         url: 'https://api.switch-bot.com/v1.0/devices',
//         headers: {
//           'Authorization': '753fc75e5a8094fd7fdd3d1ddf23817d7c72e5a16ce0a4c33f34b22aa470709db7d933946ccf72dfff08e10b60ed0545',
//         }
//       }).then((response) => {
//         let sbres = response.data
//         if (sbres.statusCode != 100) {
//           reject(new Error(sbres.message))
//         } else {
//           _self.deviceList = sbres.body.deviceList
//           _self.infraredRemoteList = sbres.body.infraredRemoteList
//           resolve(sbres.body)
//         }
//       })
//     })

// }

