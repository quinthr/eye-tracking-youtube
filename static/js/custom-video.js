//Playlist Initialize
videojs(document.querySelector("#vid1")).playlistUi();

//add Buttons
var player = videojs('vid1');
player.controlBar.addChild('Button', {
  text: 'Skip Backward',
  className: 'vjs-skip-backward-5 webgazer-clickable',
});
player.controlBar.addChild('Button', {
  text: 'Home',
  className: 'home-button webgazer-clickable',
});
console.log(player.controlBar.children)
skipBackButton = document.getElementsByClassName('vjs-skip-backward-5')[0];
playButton = document.getElementsByClassName('vjs-play-control')[0];
homeButton = document.getElementsByClassName('home-button')[0];
homeIconPlaceholder = homeButton.querySelector('.vjs-icon-placeholder');
homeButton.onclick = function() {
    document.location.href = '/';
}
skipBackButton.onclick = function() {
  var currentTime = player.currentTime();
  var targetTime = currentTime - 5;
  player.currentTime(targetTime);
};
playButton.classList.add("webgazer-clickable")
skipBackButton.style = "background-color: white; border: 1px solid #e6e6e6;"
homeButton.style = "background-color: white; border: 1px solid #e6e6e6; cursor:pointer;"

// Play through the playlist automatically.
var player = videojs('vid1');
player.playlist.autoadvance(0);
player.ready(function() {
    console.log(new Date());
    player.play();
});