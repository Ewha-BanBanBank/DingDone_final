package com.example.dingdone;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.Toast;
// import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.messaging.FirebaseMessaging;

public class AlarmActivity extends AppCompatActivity {
    ImageView siren;
    Handler handler=new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alarm);

        FirebaseMessaging.getInstance().getToken()
                .addOnCompleteListener(new OnCompleteListener<String>() {
                    @Override
                    public void onComplete(@NonNull Task<String> task) {
                        if (!task.isSuccessful()) {
                            Log.w("FCM Log", "Fetching FCM registration token failed", task.getException());
                            return;
                        }

                        // Get new FCM registration token
                        String token = task.getResult();

                        Log.d("FCM Log", "FCM 토큰: "+token);
                        Toast.makeText(AlarmActivity.this, token, Toast.LENGTH_SHORT).show(); //토큰 출력
                    }
                });

        siren=(ImageView)findViewById(R.id.imageView2);
        siren.setOnClickListener(new MyListener());

        startService(new Intent(getApplicationContext(), MusicService.class));

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                Intent intent=new Intent(AlarmActivity.this, LoadingActivity.class);
                startActivity(intent);
                finish();
            }
        }, 5000);
    }

    @Override
    protected void onDestroy() {
        stopService(new Intent(getApplicationContext(), MusicService.class));
        super.onDestroy();
    }

    @Override
    protected void onUserLeaveHint() {
        super.onUserLeaveHint();
        //이벤트 작성
        // System.exit(0);
        stopService(new Intent(getApplicationContext(), MusicService.class));
    }

    class MyListener implements View.OnClickListener {
        @Override
        public void onClick(View view) {
            stopService(new Intent(getApplicationContext(), MusicService.class));
        }
    }
}