CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();


CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}


CTFd._internal.challenge.postRender = function () {
    console.log(this.data)

    document.getElementById("challenge-cur-deploy-status-text").innerHTML = "Current Deploy Status for your team: "+this.data.deploy_status;

    deploy_btn = document.getElementById("challenge-deploy-btn")
    validate_btn = document.getElementById("challenge-validate-btn")
    destroy_btn = document.getElementById("challenge-destroy-btn")

    //enable destroy button
    if(['DEPLOYED', 'FAILED_DEPLOY', 'FAILED_DESTROY'].find(this.data.deploy_status)){
        destroy_btn.classList.remove("hidden");
    }

    if(this.data.deploy_status === 'DEPLOYING') {
        deploy_btn.classList.add("hidden");
        deploy_btns = document.getElementById("deploy-btns")
        deploy_btns.classList.add("hidden");

        loader = document.getElementById("deploy-loader")
        loader.classList.remove("hidden");
    }else if(this.data.deploy_status === 'DEPLOYED'){
        validate_btn.classList.remove("hidden");
    }else if(this.data.deploy_status !== 'NOT_DEPLOYED'){
        deploy_btn.classList.add("hidden");
        deploy_btn.title = "You can only deploy when the status is NOT_DEPLOYED"
    }else{//it is NOT_DEPLOYED

    }
}


CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission = CTFd.lib.$('#challenge-input').val()

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};

function deploy_challenge(challenge_id) {
    fetch("/plugins/byoa_challenges/deploy/"+challenge_id, {
        method: "GET",
        headers: {
            'Accept': 'application/json'
        },
    }).then(response => response.json())
        .then(data => document.getElementById("test").innerHTML=data.Note);
}
