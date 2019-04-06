let grados2Radianes = (grados) => {
    grados = ( grados < 0 ? 360 - grados : grados );
    return grados * Math.PI / 180
};
let animatedSpeedometer = null;
class Speedometer {
    constructor( height, idcanvas, maximo = 100, pasos = 10, extra = 20, unit = "%" ) {
        this.extra = extra;
        this.pasos = pasos;
        this.unit = unit;
        this.height = height;
        this.width = height * 2;
        this.center = { x : this.width / 2, y : this.height };
        let c = document.getElementById( idcanvas );
        c.width = this.width;
        c.height = this.height + this.extra;
        this.canvas = c.getContext( "2d" );
        this.canvas.scale( 1, 1);
        this.speedGradient = this.canvas.createLinearGradient( 0, this.height, 0, 0 );
        this.speedGradient.addColorStop( 0, "#41dcf4" );
        this.speedGradient.addColorStop( 0, "#00b8fe" );
        this.maximo = maximo;
    }
    dibujar( vel ) {
        vel = Math.abs( Math.floor( vel ) );
        if( vel > this.maximo ) {
            vel = this.maximo;
        }

        this.canvas.clearRect( 0, 0, this.width, this.height + this.extra );

        this.canvas.beginPath();
        this.canvas.fillStyle = 'rgba( 0, 0, 0, 0.9 )';
        this.canvas.arc( this.center.x, this.center.y, this.width / ( 25 / 12 ), 0, 2 * Math.PI);
        this.canvas.fill();
        this.canvas.fillStyle = "#ffffff";
        this.canvas.stroke();

        this.canvas.beginPath();
        this.canvas.strokeStyle = "#333333";
        this.canvas.lineWidth = this.width / 80;
        this.canvas.arc( this.center.x, this.center.y, this.width / 5, 0, 2 * Math.PI );
        this.canvas.stroke();

        this.canvas.beginPath();
        this.canvas.lineWidth = 1;
        this.canvas.arc( this.center.x, this.center.y, this.width / ( 25 / 12 ), 0, Math.PI, true );
        this.canvas.stroke();

        this.canvas.textAlign = "center";
        this.canvas.font = `${this.width / ( 80 / 7 )}px MuseoSans_900-webfont`;
        this.canvas.fillText( `${vel}${this.unit}`, this.center.x, this.center.y / ( 25 / 23 ) );

        //this.canvas.font = `${this.width / ( 160 / 9 )}px MuseoSans_900-webfont`;
        //this.canvas.fillText( this.unit, this.center.x, this.center.y / ( 25 / 26 ) );

        this.canvas.fillStyle = "#ffffff";

        this.canvas.save();

        for( let i = 0; i <= this.pasos; i++ ) {
            let grados_rotacion = i * ( 180 / this.pasos ) + 180;
            this.dibujarMiniNeedle( grados2Radianes( grados_rotacion ), i % 2 == 0 ? 3 : 1, i % 2 == 0 ? Math.ceil( i * this.maximo / this.pasos ) : '' );
        }

        this.canvas.restore();

        this.canvas.beginPath();
        this.canvas.lineWidth = this.width / 20;
        this.canvas.shadowBlur = this.width / 25;
        this.canvas.shadowColor = "#00c6ff";
        this.canvas.strokeStyle = this.speedGradient;
        this.canvas.arc( this.center.x, this.center.y, this.width / ( 125 / 57 ), Math.PI, Math.PI + ( vel * Math.PI / this.maximo ) );
        this.canvas.stroke();

        this.canvas.shadowBlur = 0;
        this.canvas.strokeStyle = "#41dcf4";
        this.canvas.lineWidth = 2;
        this.canvas.save();
        this.canvas.translate( this.center.x, this.center.y );
        this.canvas.rotate( Math.PI + ( vel * Math.PI / this.maximo ) );
        this.canvas.strokeRect( this.width / ( 25 / 12 ), 0, -this.width / ( 100 / 27 ), 1 );
        this.canvas.restore();

        this.canvas.beginPath();
        this.canvas.strokeStyle = "#00b8fe";
        this.canvas.lineWidth = this.width / 80;
        this.canvas.arc( this.center.x, this.center.y, this.width / ( 25 / 12 ), 0, 2 * Math.PI );
        this.canvas.stroke();
    }
    dibujarMiniNeedle( rotacion, ancho, indicador ){
        let radio = this.width / ( 27 / 12 );
        let mark = {
            ancho : this.width / 25,
            alto : 1,
            x : -radio,
            y : 0
        };
        radio = this.width / ( 34 / 12 );
        let label_position = {
            x : radio * Math.cos( rotacion ),
            y : radio * Math.sin( rotacion )
        }
        this.canvas.lineWidth = ancho;
        this.canvas.strokeStyle = "#333333";
        this.canvas.fillStyle = "#333333";
        rotacion -= Math.PI;
        this.canvas.translate( this.center.x, this.center.y );
        this.canvas.rotate( rotacion );
        this.canvas.strokeRect( mark.x, mark.y, mark.ancho, mark.alto );
        this.canvas.rotate( -rotacion );
        this.canvas.font = `${this.width / 20}px MuseoSans_900-webfont`;
        this.canvas.fillStyle = "#FFF";
        this.canvas.translate( 0, ( this.width / 20 ) / 2 );
        this.canvas.fillText( indicador, label_position.x, label_position.y );
        this.canvas.translate( 0, -( this.width / 20 ) / 2 );
        this.canvas.translate( -this.center.x, -this.center.y );
    }
    animate( vel ) {
        vel = Math.abs( Math.floor( vel ) );
        if( vel > this.maximo ) {
            vel = this.maximo;
        }
        this.animation = {
            milliseconds : 50,
            inc_vel : 1,
            current_vel : 0,
            max_vel : vel
        }
        animatedSpeedometer = this;
        animatedSpeedometer.animationStep();
    }
    animationStep() {
        animatedSpeedometer.dibujar( animatedSpeedometer.animation.current_vel );
        animatedSpeedometer.animation.current_vel += animatedSpeedometer.animation.inc_vel;
        if( animatedSpeedometer.animation.current_vel <= animatedSpeedometer.animation.max_vel ) {
            window.setTimeout( animatedSpeedometer.animationStep, animatedSpeedometer.animation.milliseconds );
        }
    }
}